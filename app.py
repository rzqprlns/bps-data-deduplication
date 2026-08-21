import pandas as pd
import streamlit as st

from cleaning import clean_dataset
from deduplication import run_deduplication


st.set_page_config(
    page_title="Record Deduplication Demo",
    page_icon="◼",
    layout="wide"
)


# =========================
# CUSTOM STYLE
# =========================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Libre+Baskerville:wght@400;700&display=swap');

    html, body, [class*="css"]  {
        background-color: #F4F6F8;
        color: #18233A;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 3rem;
        padding-bottom: 5rem;
    }

    h1, h2, h3 {
        font-family: 'Libre Baskerville', serif !important;
        color: #17233B !important;
    }

    p, div, span, label {
        font-family: 'DM Mono', monospace;
    }

    .eyebrow {
        font-family: 'DM Mono', monospace;
        font-size: 0.95rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #3F7F73;
        margin-bottom: 0.8rem;
    }

    .hero-title {
        font-family: 'Libre Baskerville', serif;
        font-size: 3.5rem;
        line-height: 1.15;
        font-weight: 700;
        color: #17233B;
        margin-bottom: 1rem;
    }

    .hero-subtitle {
        font-family: 'DM Mono', monospace;
        font-size: 1rem;
        color: #5A667A;
        line-height: 1.8;
        max-width: 800px;
        margin-bottom: 2rem;
    }

    .metric-wrap {
        border-top: 1px solid #C9D0D8;
        border-bottom: 1px solid #C9D0D8;
        padding: 1.4rem 0;
        margin: 1.5rem 0 2.5rem 0;
    }

    .metric-value {
        font-family: 'DM Mono', monospace;
        font-size: 2rem;
        font-weight: 500;
        color: #17233B;
    }

    .metric-label {
        font-family: 'DM Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 0.08em;
        color: #6C7688;
        text-transform: uppercase;
    }

    .section-label {
        font-family: 'DM Mono', monospace;
        font-size: 0.85rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #B8892E;
        margin-top: 3rem;
        margin-bottom: 0.4rem;
    }

    .section-title {
        font-family: 'Libre Baskerville', serif;
        font-size: 2rem;
        color: #17233B;
        margin-bottom: 1rem;
    }

    .note-box {
        background: #E6F0ED;
        border-left: 4px solid #3F7F73;
        padding: 1rem 1.2rem;
        margin: 1rem 0 2rem 0;
        font-family: 'DM Mono', monospace;
        color: #315C55;
    }

    div.stButton > button {
        background-color: #17233B;
        color: #FFFFFF;
        border: 1px solid #17233B;
        border-radius: 0px;
        padding: 0.75rem 1.2rem;
        font-family: 'DM Mono', monospace;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        transition: 0.2s;
    }

    div.stButton > button:hover {
        background-color: #F4F6F8;
        color: #17233B;
        border: 1px solid #17233B;
    }

    div[data-testid="stDownloadButton"] button {
        border-radius: 0px;
        font-family: 'DM Mono', monospace;
    }

    div[data-testid="stMetric"] {
        background: transparent;
        border: 1px solid #D5DBE2;
        padding: 1rem;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #D5DBE2;
    }

    section[data-testid="stSidebar"] {
        background-color: #EEF1F5;
        border-right: 1px solid #D5DBE2;
    }

    .small {
        font-family: 'DM Mono', monospace;
        color: #6C7688;
        font-size: 0.85rem;
        line-height: 1.7;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)


# =========================
# HERO
# =========================
st.markdown(
    """
    <div class="eyebrow">DATA QUALITY · RECORD LINKAGE</div>

    <div class="hero-title">
        Large-Scale Record<br>
        Deduplication
    </div>

    <div class="hero-subtitle">
        An interactive reconstruction of a Python-based workflow used to
        standardize and deduplicate large operational datasets.
        The original project processed more than 191K records.
    </div>
    """,
    unsafe_allow_html=True
)


m1, m2, m3 = st.columns(3)

with m1:
    st.markdown(
        """
        <div class="metric-value">191K+</div>
        <div class="metric-label">Records Processed</div>
        """,
        unsafe_allow_html=True
    )

with m2:
    st.markdown(
        """
        <div class="metric-value">46K+</div>
        <div class="metric-label">Duplicates Removed</div>
        """,
        unsafe_allow_html=True
    )

with m3:
    st.markdown(
        """
        <div class="metric-value">3</div>
        <div class="metric-label">Matching Rules</div>
        """,
        unsafe_allow_html=True
    )


st.markdown(
    """
    <div class="note-box">
    This public demo uses synthetic data only.
    No confidential or original BPS data is included.
    </div>
    """,
    unsafe_allow_html=True
)


# =========================
# DATA SOURCE
# =========================
@st.cache_data
def load_sample_data():
    return pd.read_csv("synthetic_bps_dedup_raw.csv")


st.sidebar.markdown("## Demo Controls")

data_source = st.sidebar.radio(
    "Data source",
    ["Sample dataset", "Upload CSV"]
)


if data_source == "Sample dataset":
    df = load_sample_data()

else:
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV",
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
        "Dataset must contain: record_id, nama_usaha, alamat, kecamatan"
    )
    st.stop()


# =========================
# STEP 01
# =========================
st.markdown(
    """
    <div class="section-label">STEP 01 · RAW DATA</div>
    <div class="section-title">Inspect the Input</div>
    """,
    unsafe_allow_html=True
)


c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Records", f"{len(df):,}")

with c2:
    st.metric("Kecamatan", df["kecamatan"].nunique())

with c3:
    st.metric("Columns", len(df.columns))


st.dataframe(
    df.head(20),
    use_container_width=True,
    hide_index=True
)


# =========================
# STEP 02
# =========================
st.markdown(
    """
    <div class="section-label">STEP 02 · STANDARDIZATION</div>
    <div class="section-title">Normalize Names & Addresses</div>

    <div class="small">
    Address formatting is standardized before duplicate detection,
    including street notation, house numbers, RT/RW, punctuation,
    capitalization, and whitespace.
    </div>
    """,
    unsafe_allow_html=True
)


if st.button("Run Standardization"):

    cleaned_df = clean_dataset(df)
    st.session_state["cleaned_df"] = cleaned_df


if "cleaned_df" in st.session_state:

    cleaned_df = st.session_state["cleaned_df"]

    comparison = cleaned_df[
        [
            "nama_usaha",
            "nama_normalized",
            "alamat",
            "alamat_normalized"
        ]
    ].head(20)

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )


# =========================
# STEP 03
# =========================
st.markdown(
    """
    <div class="section-label">STEP 03 · DUPLICATE DETECTION</div>
    <div class="section-title">Identify Duplicate Groups</div>

    <div class="small">
    Records are evaluated within the same kecamatan using normalized
    name, normalized address, and their combination.
    </div>
    """,
    unsafe_allow_html=True
)


if "cleaned_df" not in st.session_state:

    st.info("Run standardization first.")

else:

    if st.button("Detect Duplicates"):

        result = run_deduplication(
            st.session_state["cleaned_df"]
        )

        st.session_state["dedup_result"] = result


# =========================
# RESULTS
# =========================
if "dedup_result" in st.session_state:

    result = st.session_state["dedup_result"]

    removed_duplicates = result[
        result["is_redundant_duplicate"]
    ]

    unique_records = result[
        ~result["is_redundant_duplicate"]
    ]

    duplicate_rate = (
        len(removed_duplicates) / len(result) * 100
    )


    st.markdown(
        """
        <div class="section-label">STEP 04 · RESULTS</div>
        <div class="section-title">Review the Output</div>
        """,
        unsafe_allow_html=True
    )


    r1, r2, r3, r4 = st.columns(4)

    with r1:
        st.metric(
            "Processed",
            f"{len(result):,}"
        )

    with r2:
        st.metric(
            "Unique Kept",
            f"{len(unique_records):,}"
        )

    with r3:
        st.metric(
            "Duplicates Removed",
            f"{len(removed_duplicates):,}"
        )

    with r4:
        st.metric(
            "Duplicate Rate",
            f"{duplicate_rate:.1f}%"
        )


    st.markdown("### Duplicate Records")

    duplicate_view = result[
        result["duplicate_name_address"]
    ][
        [
            "record_id",
            "nama_usaha",
            "alamat",
            "kecamatan",
            "duplicate_group_id",
            "duplicate_group_size",
            "is_redundant_duplicate"
        ]
    ]

    st.dataframe(
        duplicate_view.head(100),
        use_container_width=True,
        hide_index=True
    )


    st.markdown("### Largest Duplicate Groups")

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
        duplicate_groups.head(30),
        use_container_width=True,
        hide_index=True
    )


    st.markdown("### Export")

    cleaned_csv = unique_records.to_csv(
        index=False
    ).encode("utf-8")

    duplicate_csv = removed_duplicates.to_csv(
        index=False
    ).encode("utf-8")


    d1, d2 = st.columns(2)

    with d1:
        st.download_button(
            "Download Clean Dataset",
            cleaned_csv,
            "clean_dataset.csv",
            "text/csv"
        )

    with d2:
        st.download_button(
            "Download Removed Duplicates",
            duplicate_csv,
            "duplicate_records.csv",
            "text/csv"
        )


st.markdown("---")

st.markdown(
    """
    <div class="small">
    Portfolio reconstruction by <strong>Rizqi Aprilianes</strong><br>
    Python · Pandas · Regex · Data Quality
    </div>
    """,
    unsafe_allow_html=True
    )
