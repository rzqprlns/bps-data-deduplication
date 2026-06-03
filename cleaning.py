import pandas as pd  # type: ignore
import numpy as np   # type: ignore
import re
import logging
import time

try:
    from rapidfuzz import fuzz  # type: ignore
except ImportError as e:
    raise ImportError(f"Required dependencies not found. Please install: pandas, numpy, rapidfuzz\nError: {e}")

# Konfigurasi Logging standar industri
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SBRDataPipeline:
    """
    End-to-End Pipeline untuk Pembersihan, Filter Wilayah, dan Deduplikasi Bertahap.
    Dioptimalkan dengan teknik 'Column Pruning' untuk efisiensi memori.
    """

    def __init__(self, df: pd.DataFrame):
        # 1. Simpan salinan data asli utuh (tanpa diubah)
        self.df_raw = df.copy()
        
        # Buat dummy ID jika tidak ada (untuk proses merge nanti)
        if 'record_id' not in self.df_raw.columns:
            self.df_raw['record_id'] = range(1, len(self.df_raw) + 1)

        logging.info(f"Dimensi Data Asli: {self.df_raw.shape}")

        # 2. COLUMN PRUNING: Ambil HANYA kolom yang dibutuhkan untuk proses evaluasi
        # Sesuaikan nama kolom ini jika berbeda di datamu
        kolom_penting = ['record_id', 'nama_usaha', 'alamat_usaha', 'kdkec', 'skala_usaha']
        
        # Pastikan kolom yang diminta benar-benar ada di dataframe
        kolom_tersedia = [col for col in kolom_penting if col in self.df_raw.columns]
        
        # DataFrame inilah yang akan diproses (jauh lebih ringan)
        self.df = self.df_raw[kolom_tersedia].copy()

        # Menyiapkan kolom output
        self.df['status_evaluasi'] = "Aman (Unik)"
        self.df['keterangan_detail'] = ""

    def _clean_text(self, text: str) -> str:
        if pd.isna(text): return ""
        text = str(text).lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return re.sub(r'\s+', ' ', text).strip()

    def step_1_preprocessing(self):
        logging.info("Step 1: Normalisasi teks nama dan alamat...")
        self.df['nama_clean'] = self.df.get('nama_usaha', pd.Series(dtype=str)).apply(self._clean_text)
        self.df['alamat_clean'] = self.df.get('alamat_usaha', pd.Series(dtype=str)).apply(self._clean_text)
        return self

    def step_2_filter_kota_bogor(self):
        logging.info("Step 2: Memvalidasi alamat dalam Kota Bogor...")
        def cek_bogor(teks):
            if not teks: return False
            if re.search(r'\b(kab\.|kab|kabupaten|reg\.|regency)\s*bogor\b', teks): return False
            if re.search(r'\b(kota|city)\s*bogor\b', teks): return True
            pola_kecamatan = r'\bbogor\s*(barat|selatan|tengah|timur|utara)\b|\btanah\s*sareal\b'
            if re.search(pola_kecamatan, teks): return True
            return False 

        self.df['is_kota_bogor'] = self.df['alamat_clean'].apply(cek_bogor)
        mask_luar = ~self.df['is_kota_bogor']
        self.df.loc[mask_luar, 'status_evaluasi'] = "Tidak Ditemukan (Luar Wilayah)"
        return self

    def step_3_ekstrak_dan_evaluasi_rtrw(self):
        logging.info("Step 3: Ekstraksi RT/RW dan Evaluasi Skala Usaha...")
        self.df['rt_ext'] = self.df['alamat_clean'].str.extract(r'rt\s*\.?\s*0*(\d+)')
        self.df['rw_ext'] = self.df['alamat_clean'].str.extract(r'rw\s*\.?\s*0*(\d+)')

        mask_rtrw_kosong = self.df['rt_ext'].isna() & self.df['rw_ext'].isna()
        
        if 'skala_usaha' in self.df.columns:
            mask_ub_dll = mask_rtrw_kosong & self.df['skala_usaha'].isin(['UB', 'Hotel', 'Rumah Sakit'])
            self.df.loc[mask_ub_dll, 'status_evaluasi'] = "Perlu Cek Manual (UB/Fasilitas tanpa RT/RW)"
            
            mask_umk = mask_rtrw_kosong & (self.df['skala_usaha'] == 'UMK')
            self.df.loc[mask_umk, 'status_evaluasi'] = "Sulit Dikonfirmasi (UMK tanpa RT/RW)"

        return self

    def step_4_deduplikasi_kompleks(self, fuzzy_threshold=85):
        logging.info("Step 4: Memulai Analisis Deduplikasi Multi-Tahap (Fuzzy Matching)...")
        
        df_valid = self.df[self.df['status_evaluasi'] == "Aman (Unik)"].copy()
        blocks = df_valid.groupby('kdkec') if 'kdkec' in df_valid.columns else [('All', df_valid)]

        total_blocks = len(blocks)
        logging.info(f"Total blok wilayah (Kecamatan) yang akan diproses: {total_blocks} blok.")

        for idx, (block_name, block_df) in enumerate(blocks, 1):
            total_records = len(block_df)
            
            if total_records < 2:
                logging.info(f"-> Blok {idx}/{total_blocks} (Kecamatan {block_name}): Di-skip (Hanya {total_records} data)")
                continue

            # Log untuk menandai dimulainya blok baru
            logging.info(f"-> Blok {idx}/{total_blocks} (Kecamatan {block_name}): Memulai perbandingan {total_records} data...")

            records = block_df[['record_id', 'nama_clean', 'alamat_clean']].to_dict('records')
            processed = set()

            for i in range(total_records):
                # LOGGING INTERNAL: Menampilkan log setiap kelipatan 1000 baris agar tidak dikira hang
                if i > 0 and i % 1000 == 0:
                    logging.info(f"   ... Progress Blok {idx}: {i} dari {total_records} baris telah dievaluasi.")

                rec_a = records[i]
                if rec_a['record_id'] in processed: continue

                for j in range(i + 1, total_records):
                    rec_b = records[j]
                    if rec_b['record_id'] in processed: continue

                    nama_exact = (rec_a['nama_clean'] == rec_b['nama_clean']) and rec_a['nama_clean'] != ""
                    alamat_exact = (rec_a['alamat_clean'] == rec_b['alamat_clean']) and rec_a['alamat_clean'] != ""

                    if nama_exact and alamat_exact:
                        self._flag_record(rec_b['record_id'], "GANDA IDENTIK", f"Sama dengan ID {rec_a['record_id']}")
                        processed.add(rec_b['record_id'])
                        continue

                    if alamat_exact and not nama_exact:
                        self._flag_record(rec_b['record_id'], "ALAMAT GANDA", f"Potensi Ganti Usaha dari ID {rec_a['record_id']}")
                        self._flag_record(rec_a['record_id'], "ALAMAT GANDA", f"Tercatat juga di ID {rec_b['record_id']}")
                        continue

                    if nama_exact and not alamat_exact:
                        self._flag_record(rec_b['record_id'], "NAMA GANDA", f"Potensi Cabang/Pindah dari ID {rec_a['record_id']}")
                        continue

                    nama_score = fuzz.token_set_ratio(rec_a['nama_clean'], rec_b['nama_clean'])
                    if nama_score >= fuzzy_threshold:
                        if alamat_exact:
                            self._flag_record(rec_b['record_id'], "TYPO NAMA", f"Skor {nama_score}% dengan ID {rec_a['record_id']}")
                            processed.add(rec_b['record_id'])
                        else:
                            alamat_score = fuzz.token_set_ratio(rec_a['alamat_clean'], rec_b['alamat_clean'])
                            if alamat_score >= fuzzy_threshold:
                                self._flag_record(rec_b['record_id'], "FUZZY GANDA", f"Nama({nama_score}%) Alamat({alamat_score}%) dgn ID {rec_a['record_id']}")
                                processed.add(rec_b['record_id'])

            logging.info(f"-> Blok {idx}/{total_blocks} Selesai.")

        logging.info("Deduplikasi Selesai.")
        return self

    def _flag_record(self, record_id, status, keterangan):
        mask = self.df['record_id'] == record_id
        current_status = self.df.loc[mask, 'status_evaluasi'].values[0]
        if current_status == "Aman (Unik)" or current_status == "ALAMAT GANDA":
            self.df.loc[mask, 'status_evaluasi'] = status
            self.df.loc[mask, 'keterangan_detail'] = keterangan
            
    def finalize_and_merge(self):
        """
        Step Terakhir: Menggabungkan hasil evaluasi (status) kembali dengan data asli yang utuh.
        """
        logging.info("Finalisasi: Menyatukan hasil evaluasi dengan data asli...")
        
        # Ambil HANYA kolom hasil (record_id, status_evaluasi, keterangan_detail)
        df_hasil = self.df[['record_id', 'status_evaluasi', 'keterangan_detail']]
        
        # Gabungkan ke data asli berdasarkan record_id
        df_final = pd.merge(self.df_raw, df_hasil, on='record_id', how='left')
        
        logging.info(f"Dimensi Data Final: {df_final.shape}")
        return df_final


# ==========================================
# EKSEKUSI PIPELINE
# ==========================================
if __name__ == "__main__":
    start_time = time.time()
    
    # 1. Panggil class dengan data raw (Pastikan sep=";" sesuai data SBR)
    df = pd.read_csv("dummy_data_bogor.csv", sep=";")  
    
    pipeline = SBRDataPipeline(df)

    # 2. Jalankan semua tahapan (Method Chaining)
    pipeline = (pipeline
                 .step_1_preprocessing()
                 .step_2_filter_kota_bogor()
                 .step_3_ekstrak_dan_evaluasi_rtrw()
                 .step_4_deduplikasi_kompleks(fuzzy_threshold=85))
    
    # 3. Satukan kembali hasilnya
    df_final = pipeline.finalize_and_merge()

    # 4. Export hasil akhir
    logging.info("Mengekspor ke Excel...")
    df_final.to_excel("SBR_Triage_Result.xlsx", index=False)
    
    end_time = time.time()
    logging.info(f"Semua proses selesai dalam {round(end_time - start_time, 2)} detik.")