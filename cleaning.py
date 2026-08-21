import re
import pandas as pd


INPUT_FILE = "synthetic_bps_dedup_raw.csv"
OUTPUT_FILE = "synthetic_bps_dedup_cleaned.csv"


def normalize_name(value):
    """
    Standardize business names by:
    - converting to uppercase
    - removing selected punctuation
    - trimming extra spaces
    """
    if pd.isna(value):
        return ""

    value = str(value).upper().strip()
    value = re.sub(r"[.,;:()]", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value


def normalize_address(value):
    """
    Standardize address formatting:
    - JL / JLN -> JALAN
    - NO -> NOMOR
    - RT/RW formatting
    - punctuation
    - extra spaces
    """
    if pd.isna(value):
        return ""

    value = str(value).upper().strip()

    # Street notation
    value = re.sub(r"\bJLN\.?\b", "JALAN", value)
    value = re.sub(r"\bJL\.?\b", "JALAN", value)

    # House number notation
    value = re.sub(r"\bNO\.?\b", "NOMOR", value)

    # Remove punctuation
    value = re.sub(r"[,;:]", " ", value)
    value = value.replace("/", " ")

    # Standardize RT
    value = re.sub(
        r"\bRT\.?\s*0*(\d{1,2})\b",
        lambda match: f"RT {int(match.group(1)):02d}",
        value,
    )

    # Standardize RW
    value = re.sub(
        r"\bRW\.?\s*0*(\d{1,2})\b",
        lambda match: f"RW {int(match.group(1)):02d}",
        value,
    )

    # Handle addresses where house number appears
    # without the word NOMOR
    if "NOMOR" not in value:
        value = re.sub(
            r"^(JALAN\s+.+?)\s+(\d+)\s+(RT\s+\d{2})",
            r"\1 NOMOR \2 \3",
            value,
        )

    # Remove extra spaces
    value = re.sub(r"\s+", " ", value).strip()

    return value


def clean_dataset(df):
    """
    Apply all standardization steps to the dataset.
    """

    cleaned = df.copy()

    cleaned["nama_normalized"] = cleaned["nama_usaha"].apply(
        normalize_name
    )

    cleaned["alamat_normalized"] = cleaned["alamat"].apply(
        normalize_address
    )

    cleaned["kecamatan_normalized"] = (
        cleaned["kecamatan"]
        .astype(str)
        .str.upper()
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    return cleaned


if __name__ == "__main__":

    df = pd.read_csv(INPUT_FILE)

    cleaned_df = clean_dataset(df)

    cleaned_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print("Cleaning completed.")
    print(f"Rows processed : {len(cleaned_df):,}")
    print(f"Output file    : {OUTPUT_FILE}")
