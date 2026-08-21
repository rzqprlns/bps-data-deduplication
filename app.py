import pandas as pd
import streamlit as st

from cleaning import clean_dataset
from deduplication import run_deduplication


st.set_page_config(
    page_title="Record Deduplication Demo",
    page_icon="🧹",
    layout="wide"
)


st.title("Large-Scale Record Deduplication")
st.caption(
    "Interactive demo of a Python-based data cleaning and duplicate detection workflow."
)

st.info(
    "This demo uses fully synthetic data. "
    "No confidential or original BPS data is included."
)


@st.cache_data
def load_sample_data():
    return pd.read_csv("synthetic_bps_dedup_raw.csv")


st.sidebar.header("Demo Options")

data_source = st.sidebar.radio(
    "Choose data source",
    ["Use sample dataset", "Upload CSV"]
)


if data_source == "Use sample dataset":
    df = load_sample_data()

else:
    uploaded_file = st.sidebar.file_uploader(
        "Upload a CSV file",
        type=["csv"]
    )

    if uploaded_file is None:
        st.warning("Upload a CSV file to continue.")
        st.stop()

    df = pd.read_csv(uploaded_file)


required_columns = {
    "record_id",
    "nama_usaha",
    "alamat",
    "kecamatan"
}

if not required_columns.issubset(df.columns):
    st.error(
        "Dataset must contain these columns: "
        "record_id, nama_usaha, alamat, kecamatan"
    )
    st.stop()


st.subheader("1. Raw Data")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Records",
        f"{len(df):,}"
    )

with col2:
    st.metric(
        "Kecamatan",
        df["kecamatan"].nunique()
    )

with col3:
    st.metric(
        "Columns",
        len(df.columns)
    )


st.dataframe(
    df.head(50),
    use_container_width=True
)


st.divider()


st.subheader("2. Data Standardization")

if st.button("Standardize Data", type="primary"):

    cleaned_df = clean_dataset(df)

    st.session_state["cleaned_df"] = cleaned_df


if "cleaned_df" in st.session_state:

    cleaned_df = st.session_state["cleaned_df"]

    before_after = cleaned_df[
        [
            "nama_usaha",
            "nama_normalized",
            "alamat",
            "alamat_normalized",
            "kecamatan"
        ]
    ].head(30)

    st.dataframe(
        before_after,
        use_container_width=True
    )


st.divider()


st.subheader("3. Duplicate Detection")

if "cleaned_df" not in st.session_state:

    st.info(
        "Run data standardization first before detecting duplicates."
    )

else:

    if st.button("Detect Duplicates"):

        result = run_deduplication(
            st.session_state["cleaned_df"]
        )

        st.session_state["dedup_result"] = result


if "dedup_result" in st.session_state:

    result = st.session_state["dedup_result"]

    removed_duplicates = result[
        result["is_redundant_duplicate"]
    ]

    unique_records = result[
        ~result["is_redundant_duplicate"]
    ]

    duplicate_rate = (
        len(removed_duplicates)
        / len(result)
        * 100
    )

    st.subheader("Results")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Records Processed",
            f"{len(result):,}"
        )

    with col2:
        st.metric(
            "Unique Records Kept",
            f"{len(unique_records):,}"
        )

    with col3:
        st.metric(
            "Duplicates Removed",
            f"{len(removed_duplicates):,}"
        )

    with col4:
        st.metric(
            "Duplicate Rate",
            f"{duplicate_rate:.1f}%"
        )


    st.subheader("Duplicate Records")

    duplicate_view = result[
        result["duplicate_name_address"]
    ][
        [
            "record_id",
            "nama_usaha",
            "alamat",
            "kecamatan",
            "nama_normalized",
            "alamat_normalized",
            "duplicate_group_id",
            "duplicate_group_size",
            "is_redundant_duplicate"
        ]
    ]

    st.dataframe(
        duplicate_view,
        use_container_width=True
    )


    st.subheader("Duplicate Groups")

    duplicate_groups = (
        result[
            result["duplicate_group_size"] > 1
        ]
        .groupby(
            [
                "kecamatan_normalized",
                "nama_normalized",
                "alamat_normalized",
                "duplicate_group_id"
            ]
        )
        .size()
        .reset_index(name="records_in_group")
        .sort_values(
            "records_in_group",
            ascending=False
        )
    )

    st.dataframe(
        duplicate_groups.head(50),
        use_container_width=True
    )


    st.subheader("Download Results")

    cleaned_csv = unique_records.to_csv(
        index=False
    ).encode("utf-8")

    duplicate_csv = removed_duplicates.to_csv(
        index=False
    ).encode("utf-8")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "Download Clean Dataset",
            cleaned_csv,
            "clean_dataset.csv",
            "text/csv"
        )

    with col2:
        st.download_button(
            "Download Removed Duplicates",
            duplicate_csv,
            "duplicate_records.csv",
            "text/csv"
        )


st.divider()

st.caption(
    "Portfolio reconstruction of a real-world data cleaning and "
    "deduplication workflow. Public demo uses synthetic data only."
  )
