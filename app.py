import pandas as pd
import streamlit as st

from cleaning import clean_dataset
from deduplication import run_deduplication


st.set_page_config(
    page_title="Data Deduplication Lab",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# VISUAL SYSTEM
# =========================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
    --cream:#fffaf2;
    --ink:#18212f;
    --muted:#6f7480;
    --blue:#4169e1;
    --yellow:#ffd95a;
    --mint:#ccefe3;
    --line:#ded8cf;
}

html, body, [class*="css"] {
    font-family:'DM Sans',sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 92% 4%, #e9eeff 0, transparent 23%),
        radial-gradient(circle at 4% 18%, #fff2b8 0, transparent 20%),
        var(--cream);
    color:var(--ink);
}

.block-container {
    max-width:1100px;
    padding-top:2rem;
    padding-bottom:5rem;
}

h1 {
    font-family:'DM Sans',sans-serif !important;
    font-weight:700 !important;
    letter-spacing:-0.055em !important;
    line-height:0.98 !important;
}

h2, h3 {
    font-family:'DM Sans',sans-serif !important;
    font-weight:700 !important;
    letter-spacing:-0.03em !important;
}

p {
    color:var(--muted);
    line-height:1.75;
}

div[data-testid="stMetric"] {
    background:rgba(255,255,255,.72);
    border:1px solid var(--ink);
    padding:1rem;
    min-height:108px;
}

div[data-testid="stMetricLabel"] {
    font-family:'IBM Plex Mono',monospace;
    text-transform:uppercase;
    letter-spacing:.05em;
    font-size:.68rem;
}

div[data-testid="stMetricValue"] {
    font-weight:700;
    letter-spacing:-.03em;
}

div[data-testid="stDataFrame"] {
    border:1px solid var(--line);
}

div.stButton > button {
    border-radius:0;
    border:1px solid var(--ink);
    background:var(--ink);
    color:white;
    padding:.75rem 1rem;
    font-family:'IBM Plex Mono',monospace;
    text-transform:uppercase;
    letter-spacing:.04em;
}

div.stButton > button:hover {
    background:var(--yellow);
    color:var(--ink);
    border-color:var(--ink);
}

div[data-testid="stDownloadButton"] > button {
    width:100%;
    border-radius:0;
    border:1px solid var(--ink);
    font-family:'IBM Plex Mono',monospace;
}

div[data-testid="stExpander"] {
    border:1px solid var(--line);
    border-radius:0;
    background:rgba(255,255,255,.55);
}

hr {
    border:none;
    border-top:1px solid var(--line);
    margin:3.2rem 0;
}

header[data-testid="stHeader"] {
    background:transparent;
}

#MainMenu, footer {
    visibility:hidden;
}

@media(max-width:760px) {
    .block-container {
        padding-left:1rem;
        padding-right:1rem;
        padding-top:1.4rem;
    }

    h1 {
        font-size:3.35rem !important;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# HELPERS
# =========================================================

@st.cache_data
def load_sample_data():
    return pd.read_csv("synthetic_bps_dedup_raw.csv")


def label(text):
    st.caption(text.upper())


# =========================================================
# HERO
# =========================================================

label("Rizqi / Data Lab · 01")

st.title("Messy records.\nCleaner decisions.")

st.write(
    """
An interactive reconstruction of a large-scale data-cleaning workflow
used to standardize inconsistent operational records and identify
repeated observations.
"""
)

hero1, hero2, hero3, hero4 = st.columns(4)

with hero1:
    st.metric("Original records", "191K+")

with hero2:
    st.metric("Duplicates removed", "46K+")

with hero3:
    st.metric("Matching checks", "3")

with hero4:
    st.metric("Primary workflow", "Python")

st.info(
    "🔒 Public-safe reconstruction — this demo uses synthetic data only. "
    "No original or identifiable BPS data is included."
)


st.divider()


# =========================================================
# WORKFLOW
# =========================================================

label("The workflow")
st.header("Four simple steps.")

st.write(
    """
The logic is straightforward: inspect the raw data, standardize
different writing styles, identify duplicate groups, then keep one
representative record and remove the repeated copies.
"""
)

w1, w2, w3, w4 = st.columns(4)

with w1:
    label("01 / Input")
    st.subheader("Inspect")
    st.caption("Review raw names, addresses, and kecamatan.")

with w2:
    label("02 / Clean")
    st.subheader("Standardize")
    st.caption("Normalize common formatting differences.")

with w3:
    label("03 / Match")
    st.subheader("Group")
    st.caption("Find records representing the same entity.")

with w4:
    label("04 / Decide")
    st.subheader("Keep / Remove")
    st.caption("Retain one record and remove redundant copies.")


st.divider()


# =========================================================
# INPUT
# =========================================================

label("Step 01 · Input")
st.header("Start with raw records.")

data_source = st.radio(
    "Data source",
    ["Use sample data", "Upload CSV"],
    horizontal=True,
)

if data_source == "Use sample data":
    df = load_sample_data()
else:
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file is None:
        st.info(
            "Upload a CSV containing: record_id, nama_usaha, alamat, kecamatan."
        )
        st.stop()

    df = pd.read_csv(uploaded_file)


required_columns = {
    "record_id",
    "nama_usaha",
    "alamat",
    "kecamatan",
}

if not required_columns.issubset(df.columns):
    st.error(
        "Required columns: record_id, nama_usaha, alamat, kecamatan"
    )
    st.stop()


i1, i2, i3 = st.columns(3)

with i1:
    st.metric("Records loaded", f"{len(df):,}")

with i2:
    st.metric("Kecamatan", df["kecamatan"].nunique())

with i3:
    st.metric("Columns", len(df.columns))


with st.expander("Preview raw data", expanded=True):
    st.dataframe(
        df.head(15),
        use_container_width=True,
        hide_index=True,
    )


st.divider()


# =========================================================
# STANDARDIZATION
# =========================================================

label("Step 02 · Standardization")
st.header("Make different writing styles comparable.")

st.write(
    """
A single address can be written in several ways.
Before looking for duplicates, those superficial formatting differences
need to be standardized.
"""
)

before, arrow, after = st.columns([1, 0.15, 1])

with before:
    label("Before")
    st.code(
        "Jl. Flamboyan No. 247 RT 13/RW 3",
        language=None,
    )

with arrow:
    st.markdown("### →")

with after:
    label("After")
    st.code(
        "JALAN FLAMBOYAN NOMOR 247 RT 13 RW 03",
        language=None,
    )


if st.button("Run standardization"):
    cleaned_df = clean_dataset(df)
    st.session_state["cleaned_df"] = cleaned_df
    st.session_state.pop("dedup_result", None)


if "cleaned_df" in st.session_state:
    cleaned_df = st.session_state["cleaned_df"]

    st.success(
        f"Standardization complete — {len(cleaned_df):,} records processed."
    )

    comparison = cleaned_df[
        [
            "nama_usaha",
            "nama_normalized",
            "alamat",
            "alamat_normalized",
        ]
    ].head(15)

    with st.expander("See before → after", expanded=True):
        st.dataframe(
            comparison,
            use_container_width=True,
            hide_index=True,
        )
        st.divider()


# =========================================================
# DUPLICATE CHECK
# =========================================================

label("Step 03 · Duplicate check")
st.header("Find records that belong together.")

st.write(
    """
After standardization, records are compared within the same kecamatan.
The workflow checks normalized name, normalized address,
and their combination.
"""
)

if "cleaned_df" not in st.session_state:
    st.info("Run standardization first.")
else:
    if st.button("Find duplicate groups"):
        result = run_deduplication(
            st.session_state["cleaned_df"]
        )

        st.session_state["dedup_result"] = result


# =========================================================
# RESULT
# =========================================================

if "dedup_result" in st.session_state:
    result = st.session_state["dedup_result"].copy()

    result["Decision"] = result[
        "is_redundant_duplicate"
    ].map({
        False: "KEEP",
        True: "REMOVE",
    })

    result["Duplicate Group"] = (
        "GROUP-"
        + result["duplicate_group_id"]
        .astype(str)
        .str.zfill(4)
    )

    result["Records Found"] = result[
        "duplicate_group_size"
    ]

    removed = result[
        result["Decision"] == "REMOVE"
    ].copy()

    kept = result[
        result["Decision"] == "KEEP"
    ].copy()

    duplicate_rate = (
        len(removed) / len(result) * 100
    )

    st.divider()

    label("Step 04 · Decision")
    st.header("Keep one. Remove the repeated copies.")

    st.write(
        """
A duplicate group represents several records that resolve to the same
normalized entity. One representative record is kept; the remaining
copies are marked for removal.
"""
    )

    st.success("KEEP = representative record")
    st.warning("REMOVE = redundant copy")

    r1, r2, r3, r4 = st.columns(4)

    with r1:
        st.metric("Processed", f"{len(result):,}")

    with r2:
        st.metric("Records kept", f"{len(kept):,}")

    with r3:
        st.metric("Records removed", f"{len(removed):,}")

    with r4:
        st.metric(
            "Duplicate rate",
            f"{duplicate_rate:.1f}%"
        )


    st.subheader("Duplicate review")

    duplicate_view = result[
        result["Records Found"] > 1
    ][
        [
            "record_id",
            "nama_usaha",
            "alamat",
            "kecamatan",
            "Duplicate Group",
            "Records Found",
            "Decision",
        ]
    ].copy()

    st.dataframe(
        duplicate_view.head(100),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Duplicate Group = ID created by this demo for records that "
        "resolve to the same normalized entity. "
        "Records Found = number of records in that group."
    )


    st.subheader("Download the result")

    clean_csv = kept.to_csv(
        index=False
    ).encode("utf-8")

    removed_csv = removed.to_csv(
        index=False
    ).encode("utf-8")

    d1, d2 = st.columns(2)

    with d1:
        st.download_button(
            "Download clean dataset",
            clean_csv,
            "clean_dataset.csv",
            "text/csv",
        )

    with d2:
        st.download_button(
            "Download removed duplicates",
            removed_csv,
            "duplicate_records.csv",
            "text/csv",
        )


st.divider()


# =========================================================
# METHOD NOTE
# =========================================================

label("Method note")
st.header("Why process records by kecamatan?")

st.write(
    """
The original dataset was large. Duplicate processing was therefore
performed within each kecamatan instead of processing the entire
dataset together.

This reduced the processing workload, but it also introduced a trade-off:
a duplicate recorded under different kecamatan could potentially be missed.
"""
)


st.divider()

label("Rizqi Aprilianes · Data Quality / Automation / Analytics")
st.caption("Synthetic public reconstruction")
