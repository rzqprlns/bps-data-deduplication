import pandas as pd

INPUT_FILE = "synthetic_bps_dedup_cleaned.csv"
OUTPUT_ALL = "deduplication_results.csv"
OUTPUT_UNIQUE = "unique_records.csv"
OUTPUT_DUPLICATES = "duplicate_records_removed.csv"


def detect_duplicates(df):
    """
    Detect duplicates within the same kecamatan using:
    1. normalized name
    2. normalized address
    3. normalized name + normalized address
    """

    result = df.copy()

    # Duplicate flags within the same kecamatan
    result["duplicate_name"] = result.duplicated(
        subset=["kecamatan_normalized", "nama_normalized"],
        keep=False
    )

    result["duplicate_address"] = result.duplicated(
        subset=["kecamatan_normalized", "alamat_normalized"],
        keep=False
    )

    result["duplicate_name_address"] = result.duplicated(
        subset=[
            "kecamatan_normalized",
            "nama_normalized",
            "alamat_normalized"
        ],
        keep=False
    )

    return result


def assign_duplicate_groups(df):
    """
    Create duplicate group IDs using name + address
    within the same kecamatan.
    """

    result = df.copy()

    group_columns = [
        "kecamatan_normalized",
        "nama_normalized",
        "alamat_normalized"
    ]

    result["duplicate_group_id"] = (
        result.groupby(group_columns, sort=False)
        .ngroup()
        .add(1)
    )

    result["duplicate_group_size"] = (
        result.groupby(group_columns)["record_id"]
        .transform("size")
    )

    return result


def mark_redundant_records(df):
    """
    Keep the first representative record from each
    duplicate group and mark the remaining records
    as redundant duplicates.
    """

    result = df.copy()

    result["is_redundant_duplicate"] = result.duplicated(
        subset=[
            "kecamatan_normalized",
            "nama_normalized",
            "alamat_normalized"
        ],
        keep="first"
    )

    return result


def run_deduplication(df):
    result = detect_duplicates(df)
    result = assign_duplicate_groups(result)
    result = mark_redundant_records(result)

    return result


if __name__ == "__main__":

    df = pd.read_csv(INPUT_FILE)

    result = run_deduplication(df)

    unique_records = result[
        ~result["is_redundant_duplicate"]
    ].copy()

    removed_duplicates = result[
        result["is_redundant_duplicate"]
    ].copy()

    result.to_csv(
        OUTPUT_ALL,
        index=False,
        encoding="utf-8-sig"
    )

    unique_records.to_csv(
        OUTPUT_UNIQUE,
        index=False,
        encoding="utf-8-sig"
    )

    removed_duplicates.to_csv(
        OUTPUT_DUPLICATES,
        index=False,
        encoding="utf-8-sig"
    )

    print("=== DEDUPLICATION SUMMARY ===")
    print(f"Input records       : {len(result):,}")
    print(f"Unique records kept : {len(unique_records):,}")
    print(f"Duplicates removed  : {len(removed_duplicates):,}")
