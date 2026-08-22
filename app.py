import pandas as pd
import streamlit as st

from cleaning import clean_dataset
from deduplication import run_deduplication


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Data Deduplication Lab",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# STYLE
# =========================================================

st.markdown(
    """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

    :root {
        --cream: #FFF9F0;
        --paper: #FFFDF8;
        --ink: #18212F;
        --muted: #6D7480;
        --line: #DED8CF;

        --blue: #3A67F2;
        --blue-soft: #E8EEFF;

        --yellow: #FFD95A;
        --yellow-soft: #FFF2B8;

        --mint: #CBEFE2;
        --orange: #FF9364;
    }

    html, body, [class*="css"] {
        font-family: "DM Sans", sans-serif;
        color: var(--ink);
    }

    .stApp {
        background:
            radial-gradient(circle at 90% 4%, #E8EEFF 0, transparent 24%),
            radial-gradient(circle at 5% 20%, #FFF2B8 0, transparent 22%),
            var(--cream);
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2.8rem;
        padding-bottom: 6rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }


    /* -----------------------------------------
       TYPOGRAPHY
    ----------------------------------------- */

    .micro {
        font-family: "IBM Plex Mono", monospace;
        font-size: .78rem;
        letter-spacing: .10em;
        text-transform: uppercase;
        color: var(--blue);
        font-weight: 500;
    }

    .hero-title {
        font-size: clamp(3.1rem, 7vw, 6rem);
        line-height: .98;
        letter-spacing: -.055em;
        font-weight: 700;
        max-width: 850px;
        margin: .8rem 0 1.5rem 0;
        color: var(--ink);
    }

    .hero-copy {
        max-width: 690px;
        font-size: 1.04rem;
        line-height: 1.8;
        color: var(--muted);
    }

    .section-kicker {
        font-family: "IBM Plex Mono", monospace;
        color: var(--blue);
        letter-spacing: .10em;
        font-size: .77rem;
        text-transform: uppercase;
        margin-top: 4rem;
        margin-bottom: .55rem;
    }

    .section-heading {
        font-size: clamp(1.8rem, 4vw, 3rem);
        letter-spacing: -.035em;
        font-weight: 700;
        margin-bottom: .7rem;
    }

    .section-copy {
        color: var(--muted);
        max-width: 760px;
        line-height: 1.75;
        margin-bottom: 1.5rem;
    }


    /* -----------------------------------------
       HERO STRIP
    ----------------------------------------- */

    .data-strip {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        margin-top: 2.4rem;
        border: 1px solid var(--ink);
        background: rgba(255,255,255,.55);
    }

    .data-cell {
        padding: 1.25rem;
        border-right: 1px solid var(--ink);
    }

    .data-cell:last-child {
        border-right: 0;
    }

    .data-value {
        font-family: "IBM Plex Mono", monospace;
        font-size: 1.55rem;
        font-weight: 500;
        margin-bottom: .25rem;
    }

    .data-label {
        color: var(--muted);
        font-family: "IBM Plex Mono", monospace;
        font-size: .68rem;
        letter-spacing: .07em;
        text-transform: uppercase;
    }


    /* -----------------------------------------
       PRIVACY NOTE
    ----------------------------------------- */

    .privacy {
        margin-top: 1.3rem;
        background: var(--mint);
        border: 1px solid var(--ink);
        padding: 1rem 1.15rem;
        font-size: .87rem;
        line-height: 1.6;
    }


    /* -----------------------------------------
       PIPELINE
    ----------------------------------------- */

    .pipeline {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: .8rem;
        margin: 1.5rem 0 2rem;
    }

    .pipeline-card {
        border: 1px solid var(--line);
        background: rgba(255,255,255,.7);
        padding: 1.15rem;
        min-height: 120px;
    }

    .pipeline-no {
        font-family: "IBM Plex Mono", monospace;
        color: var(--blue);
        font-size: .72rem;
        margin-bottom: .7rem;
    }

    .pipeline-title {
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: .35rem;
    }

    .pipeline-copy {
        font-size: .78rem;
        color: var(--muted);
        line-height: 1.55;
    }


    /* -----------------------------------------
       METRICS
    ----------------------------------------- */

    div[data-testid="stMetric"] {
        border: 1px solid var(--ink);
        background: rgba(255,255,255,.72);
        padding: 1rem 1.1rem;
        min-height: 112px;
    }

    div[data-testid="stMetricLabel"] {
        font-family: "IBM Plex Mono", monospace;
        text-transform: uppercase;
        letter-spacing: .06em;
        font-size: .68rem;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.65rem;
        font-weight: 700;
        letter-spacing: -.03em;
    }


    /* -----------------------------------------
       BUTTONS
    ----------------------------------------- */

    div.stButton > button {
        border-radius: 0;
        border: 1px solid var(--ink);
        background: var(--ink);
        color: #FFFFFF;
        padding: .75rem 1.1rem;
        font-family: "IBM Plex Mono", monospace;
        font-size: .77rem;
        letter-spacing: .05em;
        text-transform: uppercase;
        transition: .16s ease;
    }

    div.stButton > button:hover {
        background: var(--yellow);
        color: var(--ink);
        border-color: var(--ink);
    }

    div[data-testid="stDownloadButton"] > button {
        width: 100%;
        border-radius: 0;
        border: 1px solid var(--ink);
        font-family: "IBM Plex Mono", monospace;
    }


    /* -----------------------------------------
       DATAFRAME
    ----------------------------------------- */

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        background: var(--paper);
    }


    /* -----------------------------------------
       BEFORE AFTER
    ----------------------------------------- */

    .transform-wrap {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        gap: 1rem;
        align-items: center;
        margin: 1.2rem 0 1.8rem;
    }

    .transform-card {
        border: 1px solid var(--ink);
        background: var(--paper);
        padding: 1.2rem;
    }

    .transform-label {
        font-family: "IBM Plex Mono", monospace;
        font-size: .68rem;
        letter-spacing: .08em;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: .55rem;
    }

    .transform-value {
        font-family: "IBM Plex Mono", monospace;
        line-height: 1.6;
        font-size: .88rem;
    }

    .transform-arrow {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--blue);
    }


    /* -----------------------------------------
       FOOTER
    ----------------------------------------- */

    .footer-note {
        border-top: 1px solid var(--line);
        margin-top: 5rem;
        padding-top: 1.5rem;
        color: var(--muted);
        font-size: .78rem;
        font-family: "IBM Plex Mono", monospace;
    }


    /* -----------------------------------------
       MOBILE
    ----------------------------------------- */

    @media(max-width: 760px) {

        .block-container {
            padding-left: 1.05rem;
            padding-right: 1.05rem;
            padding-top: 1.8rem;
        }

        .hero-title {
            font-size: 3.2rem;
        }

        .data-strip {
            grid-template-columns: 1fr 1fr;
        }

        .data-cell {
            border-bottom: 1px solid var(--ink);
        }

        .data-cell:nth-child(2) {
            border-right: 0;
        }

        .data-cell:nth-child(3),
        .data-cell:nth-child(4) {
            border-bottom: 0;
        }

        .pipeline {
            grid-template-columns: 1fr 1fr;
        }

        .transform-wrap {
            grid-template-columns: 1fr;
        }

        .transform-arrow {
            transform: rotate(90deg);
            text-align: center;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DATA
# =========================================================

@st.cache_data
def load_sample_data():
    return pd.read_csv("synthetic_bps_dedup_raw.csv")


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="micro">RIZQI / DATA LAB · 01</div>

    <div class="hero-title">
        Messy records.<br>
        Cleaner decisions.
    </div>

    <div class="hero-copy">
        An interactive reconstruction of a large-scale data cleaning
        and deduplication workflow. The original project involved
        more than 191K operational records with inconsistent names,
        addresses, and repeated observations.
    </div>

    <div class="data-strip">

        <div class="data-cell">
            <div class="data-value">191K+</div>
            <div class="data-label">Original records</div>
        </div>

        <div class="data-cell">
            <div class="data-value">46K+</div>
            <div class="data-label">Duplicates removed</div>
        </div>

        <div class="data-cell">
            <div class="data-value">3</div>
            <div class="data-label">Matching checks</div>
        </div>

        <div class="data-cell">
            <div class="data-value">Python</div>
            <div class="data-label">Primary workflow</div>
        </div>

    </div>

    <div class="privacy">
        <strong>Public-safe reconstruction.</strong>
        This interactive demo uses synthetic data only.
        No original or identifiable BPS data is included.
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# PIPELINE
# =========================================================

st.markdown(
    """
    <div class="section-kicker">TRY THE PIPELINE</div>
    <div class="section-heading">From raw text to usable records.</div>

    <div class="section-copy">
        The workflow mirrors the logic of the original processing task:
        inspect the raw CSV, standardize inconsistent text, detect repeated
        records within the same kecamatan, then preserve one representative
        record from each duplicate group.
    </div>

    <div class="pipeline">

        <div class="pipeline-card">
            <div class="pipeline-no">01 / INPUT</div>
            <div class="pipeline-title">Inspect</div>
            <div class="pipeline-copy">
                Review raw names, addresses, and district information.
            </div>
        </div>

        <div class="pipeline-card">
            <div class="pipeline-no">02 / CLEAN</div>
            <div class="pipeline-title">Standardize</div>
            <div class="pipeline-copy">
                Normalize street notation, RT/RW, numbers, punctuation,
                and capitalization.
            </div>
        </div>

        <div class="pipeline-card">
            <div class="pipeline-no">03 / MATCH</div>
            <div class="pipeline-title">Detect</div>
            <div class="pipeline-copy">
                Compare normalized name, address, and their combination.
            </div>
        </div>

        <div class="pipeline-card">
            <div class="pipeline-no">04 / OUTPUT</div>
            <div class="pipeline-title">Deduplicate</div>
            <div class="pipeline-copy">
                Keep one representative record and flag redundant copies.
            </div>
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DATA SOURCE
# =========================================================

st.markdown(
    """
    <div class="section-kicker">STEP 01 · INPUT</div>
    <div class="section-heading">Choose the dataset.</div>
    """,
    unsafe_allow_html=True
)

data_source = st.radio(
    "Data source",
    ["Use sample data", "Upload CSV"],
    horizontal=True,
    label_visibility="collapsed"
)

if data_source == "Use sample data":
    df = load_sample_data()

else:
    uploaded_file = st.file_uploader(
        "Upload CSV",
        type=["csv"]
    )

    if uploaded_file is None:
        st.info(
            "Upload a CSV containing record_id, nama_usaha, alamat, and kecamatan."
        )
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
        "Required columns: record_id, nama_usaha, alamat, kecamatan"
    )
    st.stop()


c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Records loaded", f"{len(df):,}")

with c2:
    st.metric("Kecamatan", df["kecamatan"].nunique())

with c3:
    st.metric("Columns", len(df.columns))


with st.expander("Preview raw records", expanded=True):
    st.dataframe(
        df.head(15),
        use_container_width=True,
        hide_index=True
    )
    # =========================================================
# STANDARDIZATION
# =========================================================

st.markdown(
    """
    <div class="section-kicker">STEP 02 · STANDARDIZATION</div>
    <div class="section-heading">Make inconsistent text comparable.</div>

    <div class="section-copy">
        Raw administrative text often contains formatting differences
        that represent the same information. Standardization reduces
        those superficial differences before duplicate detection.
    </div>

    <div class="transform-wrap">

        <div class="transform-card">
            <div class="transform-label">RAW ADDRESS</div>
            <div class="transform-value">
                Jl. Flamboyan No. 247 RT 13/RW 3
            </div>
        </div>

        <div class="transform-arrow">→</div>

        <div class="transform-card">
            <div class="transform-label">STANDARDIZED</div>
            <div class="transform-value">
                JALAN FLAMBOYAN NOMOR 247 RT 13 RW 03
            </div>
        </div>

    </div>
    """,
    unsafe_allow_html=True
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
            "alamat_normalized"
        ]
    ].head(15)

    with st.expander("See before → after", expanded=True):
        st.dataframe(
            comparison,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# DUPLICATE DETECTION
# =========================================================

st.markdown(
    """
    <div class="section-kicker">STEP 03 · MATCHING</div>
    <div class="section-heading">Find repeated records.</div>

    <div class="section-copy">
        Records are evaluated within the same kecamatan.
        Duplicate signals are generated from normalized names,
        normalized addresses, and their combination.
    </div>
    """,
    unsafe_allow_html=True
)


if "cleaned_df" not in st.session_state:

    st.info(
        "Run the standardization step first."
    )

else:

    if st.button("Detect duplicates"):

        result = run_deduplication(
            st.session_state["cleaned_df"]
        )

        st.session_state["dedup_result"] = result


# =========================================================
# RESULTS
# =========================================================

if "dedup_result" in st.session_state:

    result = st.session_state["dedup_result"]

    removed_duplicates = result[
        result["is_redundant_duplicate"]
    ].copy()

    unique_records = result[
        ~result["is_redundant_duplicate"]
    ].copy()

    duplicate_rate = (
        len(removed_duplicates)
        / len(result)
        * 100
    )


    st.markdown(
        """
        <div class="section-kicker">STEP 04 · OUTPUT</div>
        <div class="section-heading">Review what changed.</div>

        <div class="section-copy">
            One representative record is retained from each exact
            normalized duplicate group, while redundant copies are
            marked for removal.
        </div>
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
            "Unique kept",
            f"{len(unique_records):,}"
        )

    with r3:
        st.metric(
            "Removed",
            f"{len(removed_duplicates):,}"
        )

    with r4:
        st.metric(
            "Duplicate rate",
            f"{duplicate_rate:.1f}%"
        )


    # -----------------------------------------------------
    # DUPLICATE GROUPS
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="section-kicker">DUPLICATE REVIEW</div>
        <div class="section-heading">Inspect the grouped records.</div>
        """,
        unsafe_allow_html=True
    )


    duplicate_view = result[
        result["duplicate_group_size"] > 1
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


    # -----------------------------------------------------
    # LARGEST GROUPS
    # -----------------------------------------------------

    largest_groups = (
        result[
            result["duplicate_group_size"] > 1
        ]
        .groupby(
            [
                "duplicate_group_id",
                "kecamatan_normalized",
                "nama_normalized",
                "alamat_normalized"
            ]
        )
        .size()
        .reset_index(name="records_in_group")
        .sort_values(
            "records_in_group",
            ascending=False
        )
    )


    with st.expander("Largest duplicate groups"):

        st.dataframe(
            largest_groups.head(25),
            use_container_width=True,
            hide_index=True
        )


    # -----------------------------------------------------
    # EXPORT
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="section-kicker">EXPORT</div>
        <div class="section-heading">Take the result with you.</div>
        """,
        unsafe_allow_html=True
    )


    clean_csv = unique_records.to_csv(
        index=False
    ).encode("utf-8")

    duplicate_csv = removed_duplicates.to_csv(
        index=False
    ).encode("utf-8")


    d1, d2 = st.columns(2)

    with d1:
        st.download_button(
            "Download clean dataset",
            clean_csv,
            "clean_dataset.csv",
            "text/csv"
        )

    with d2:
        st.download_button(
            "Download removed duplicates",
            duplicate_csv,
            "duplicate_records.csv",
            "text/csv"
        )


# =========================================================
# METHOD NOTE
# =========================================================

st.markdown(
    """
    <div class="section-kicker">METHOD NOTE</div>
    <div class="section-heading">A practical assumption, not a perfect one.</div>

    <div class="section-copy">
        The original workflow partitioned records by kecamatan before
        duplicate processing to reduce the amount of data handled together.

        This improves processing efficiency, but it also creates a limitation:
        a duplicate recorded under different kecamatan could potentially
        be missed. The strategy is therefore treated as a practical blocking
        assumption rather than a universal rule.
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer-note">
        RIZQI APRILIANES · DATA QUALITY / AUTOMATION / ANALYTICS<br>
        Portfolio reconstruction · Synthetic public demo
    </div>
    """,
    unsafe_allow_html=True
             )
