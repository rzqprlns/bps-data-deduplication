import textwrap

import pandas as pd
import streamlit as st

from cleaning import clean_dataset
from deduplication import run_deduplication


# Prevent indented HTML inside multiline strings
# from being interpreted as Markdown code blocks.
_original_markdown = st.markdown


def clean_markdown(body, *args, **kwargs):
    if isinstance(body, str):
        body = textwrap.dedent(body).strip()

    return _original_markdown(
        body,
        *args,
        **kwargs
    )


st.markdown = clean_markdown

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
        --line: #DDD7CD;

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
            radial-gradient(circle at 92% 4%, #E8EEFF 0, transparent 22%),
            radial-gradient(circle at 5% 18%, #FFF2B8 0, transparent 20%),
            var(--cream);
    }

    .block-container {
        max-width: 1120px;
        padding-top: 2.3rem;
        padding-bottom: 5rem;
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


    /* TYPOGRAPHY */

    .micro {
        font-family: "IBM Plex Mono", monospace;
        font-size: .76rem;
        letter-spacing: .10em;
        text-transform: uppercase;
        color: var(--blue);
        font-weight: 500;
    }

    .hero-title {
        font-size: clamp(3rem, 7vw, 5.8rem);
        line-height: .98;
        letter-spacing: -.055em;
        font-weight: 700;
        margin: .7rem 0 1.3rem 0;
        color: var(--ink);
    }

    .hero-copy {
        max-width: 720px;
        font-size: 1.02rem;
        line-height: 1.8;
        color: var(--muted);
    }

    .section-kicker {
        font-family: "IBM Plex Mono", monospace;
        color: var(--blue);
        letter-spacing: .10em;
        font-size: .74rem;
        text-transform: uppercase;
        margin-top: 3.6rem;
        margin-bottom: .45rem;
    }

    .section-title {
        font-size: clamp(1.8rem, 4vw, 2.8rem);
        letter-spacing: -.035em;
        font-weight: 700;
        margin-bottom: .7rem;
    }

    .section-copy {
        color: var(--muted);
        max-width: 760px;
        line-height: 1.75;
        margin-bottom: 1.4rem;
    }


    /* HERO METRICS */

    .stat-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0;
        margin-top: 2rem;
        border: 1px solid var(--ink);
        background: rgba(255,255,255,.58);
    }

    .stat-card {
        padding: 1.15rem 1.1rem;
        border-right: 1px solid var(--ink);
    }

    .stat-card:last-child {
        border-right: none;
    }

    .stat-value {
        font-family: "IBM Plex Mono", monospace;
        font-size: 1.45rem;
        font-weight: 500;
        margin-bottom: .25rem;
    }

    .stat-label {
        font-family: "IBM Plex Mono", monospace;
        color: var(--muted);
        font-size: .66rem;
        text-transform: uppercase;
        letter-spacing: .06em;
    }


    /* PRIVACY */

    .privacy-note {
        margin-top: 1rem;
        padding: 1rem 1.1rem;
        background: var(--mint);
        border: 1px solid var(--ink);
        font-size: .86rem;
        line-height: 1.6;
    }


    /* PIPELINE */

    .pipeline {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: .75rem;
        margin-top: 1.4rem;
    }

    .pipe-card {
        padding: 1rem;
        border: 1px solid var(--line);
        background: rgba(255,255,255,.72);
    }

    .pipe-no {
        font-family: "IBM Plex Mono", monospace;
        color: var(--orange);
        font-size: .68rem;
        margin-bottom: .55rem;
    }

    .pipe-title {
        font-weight: 700;
        margin-bottom: .3rem;
    }

    .pipe-copy {
        color: var(--muted);
        font-size: .76rem;
        line-height: 1.55;
    }


    /* BEFORE AFTER */

    .transform-grid {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        gap: 1rem;
        align-items: center;
        margin: 1.2rem 0 1.7rem;
    }

    .transform-card {
        background: var(--paper);
        border: 1px solid var(--ink);
        padding: 1rem;
    }

    .transform-label {
        font-family: "IBM Plex Mono", monospace;
        font-size: .66rem;
        text-transform: uppercase;
        letter-spacing: .07em;
        color: var(--muted);
        margin-bottom: .5rem;
    }

    .transform-value {
        font-family: "IBM Plex Mono", monospace;
        font-size: .84rem;
        line-height: 1.55;
    }

    .arrow {
        color: var(--blue);
        font-size: 1.5rem;
        font-weight: 700;
    }


    /* RESULT STATUS */

    .legend {
        display: flex;
        gap: .6rem;
        flex-wrap: wrap;
        margin: .8rem 0 1.2rem;
    }

    .legend-item {
        font-family: "IBM Plex Mono", monospace;
        font-size: .68rem;
        border: 1px solid var(--ink);
        padding: .4rem .65rem;
    }

    .keep {
        background: var(--mint);
    }

    .remove {
        background: var(--yellow-soft);
    }


    /* BUTTONS */

    div.stButton > button {
        border-radius: 0;
        border: 1px solid var(--ink);
        background: var(--ink);
        color: white;
        padding: .72rem 1rem;
        font-family: "IBM Plex Mono", monospace;
        font-size: .75rem;
        letter-spacing: .04em;
        text-transform: uppercase;
    }

    div.stButton > button:hover {
        background: var(--yellow);
        color: var(--ink);
    }

    div[data-testid="stDownloadButton"] > button {
        width: 100%;
        border-radius: 0;
        border: 1px solid var(--ink);
        font-family: "IBM Plex Mono", monospace;
    }

    div[data-testid="stMetric"] {
        border: 1px solid var(--ink);
        background: rgba(255,255,255,.72);
        padding: 1rem;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        background: var(--paper);
    }


    /* MOBILE */

    @media(max-width: 760px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 1.6rem;
        }

        .hero-title {
            font-size: 3.2rem;
        }

        .stat-grid {
            grid-template-columns: 1fr 1fr;
        }

        .stat-card {
            border-bottom: 1px solid var(--ink);
        }

        .stat-card:nth-child(2) {
            border-right: none;
        }

        .stat-card:nth-child(3),
        .stat-card:nth-child(4) {
            border-bottom: none;
        }

        .pipeline {
            grid-template-columns: 1fr 1fr;
        }

        .transform-grid {
            grid-template-columns: 1fr;
        }

        .arrow {
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
        An interactive reconstruction of a large-scale data-cleaning
        workflow used to standardize inconsistent records and identify
        repeated observations.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="stat-grid">
        <div class="stat-card">
            <div class="stat-value">191K+</div>
            <div class="stat-label">Original records</div>
        </div>

        <div class="stat-card">
            <div class="stat-value">46K+</div>
            <div class="stat-label">Duplicates removed</div>
        </div>

        <div class="stat-card">
            <div class="stat-value">3</div>
            <div class="stat-label">Matching checks</div>
        </div>

        <div class="stat-card">
            <div class="stat-value">Python</div>
            <div class="stat-label">Primary workflow</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="privacy-note">
        <strong>Public-safe reconstruction.</strong>
        This demo uses synthetic data only.
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
    <div class="section-kicker">THE WORKFLOW</div>
    <div class="section-title">Four simple steps.</div>

    <div class="section-copy">
        The workflow is intentionally easy to follow:
        inspect the records, standardize inconsistent text,
        find duplicate groups, then keep one representative record.
    </div>

    <div class="pipeline">
        <div class="pipe-card">
            <div class="pipe-no">01 / INPUT</div>
            <div class="pipe-title">Inspect</div>
            <div class="pipe-copy">
                Review raw names, addresses, and kecamatan.
            </div>
        </div>

        <div class="pipe-card">
            <div class="pipe-no">02 / CLEAN</div>
            <div class="pipe-title">Standardize</div>
            <div class="pipe-copy">
                Normalize common formatting differences.
            </div>
        </div>

        <div class="pipe-card">
            <div class="pipe-no">03 / MATCH</div>
            <div class="pipe-title">Group</div>
            <div class="pipe-copy">
                Identify records that resolve to the same entity.
            </div>
        </div>

        <div class="pipe-card">
            <div class="pipe-no">04 / DECIDE</div>
            <div class="pipe-title">Keep / Remove</div>
            <div class="pipe-copy">
                Preserve one representative and remove redundant copies.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# STEP 01
# =========================================================

st.markdown(
    """
    <div class="section-kicker">STEP 01 · INPUT</div>
    <div class="section-title">Start with raw records.</div>
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
            "Upload a CSV with: record_id, nama_usaha, alamat, kecamatan."
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


with st.expander("Preview raw data", expanded=True):
    st.dataframe(
        df.head(15),
        use_container_width=True,
        hide_index=True
)

# =========================================================
# STEP 02
# =========================================================

st.markdown(
    """
    <div class="section-kicker">STEP 02 · STANDARDIZATION</div>
    <div class="section-title">Make different writing styles comparable.</div>

    <div class="section-copy">
        The same address can appear in several formats.
        Standardization reduces those formatting differences
        before records are compared.
    </div>

    <div class="transform-grid">
        <div class="transform-card">
            <div class="transform-label">BEFORE</div>
            <div class="transform-value">
                Jl. Flamboyan No. 247 RT 13/RW 3
            </div>
        </div>

        <div class="arrow">→</div>

        <div class="transform-card">
            <div class="transform-label">AFTER</div>
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
        f"Done — {len(cleaned_df):,} records standardized."
    )

    comparison = cleaned_df[
        [
            "nama_usaha",
            "nama_normalized",
            "alamat",
            "alamat_normalized"
        ]
    ].head(15)

    with st.expander("See the before → after comparison", expanded=True):
        st.dataframe(
            comparison,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# STEP 03
# =========================================================

st.markdown(
    """
    <div class="section-kicker">STEP 03 · DUPLICATE CHECK</div>
    <div class="section-title">Find records that belong together.</div>

    <div class="section-copy">
        After standardization, records are grouped within the same
        kecamatan using normalized name and address information.
    </div>
    """,
    unsafe_allow_html=True
)


if "cleaned_df" not in st.session_state:

    st.info(
        "Run standardization first."
    )

else:

    if st.button("Find duplicate groups"):

        result = run_deduplication(
            st.session_state["cleaned_df"]
        )

        st.session_state["dedup_result"] = result


# =========================================================
# STEP 04
# =========================================================

if "dedup_result" in st.session_state:

    result = st.session_state["dedup_result"].copy()

    result["Decision"] = result[
        "is_redundant_duplicate"
    ].map({
        False: "KEEP",
        True: "REMOVE"
    })

    result["Duplicate Group"] = (
        "GROUP-" +
        result["duplicate_group_id"]
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
        len(removed)
        / len(result)
        * 100
    )


    st.markdown(
        """
        <div class="section-kicker">STEP 04 · DECISION</div>
        <div class="section-title">Keep one. Remove the repeated copies.</div>

        <div class="section-copy">
            Each duplicate group keeps one representative record.
            The remaining repeated records are marked for removal.
        </div>

        <div class="legend">
            <div class="legend-item keep">KEEP = representative record</div>
            <div class="legend-item remove">REMOVE = redundant copy</div>
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
            "Records kept",
            f"{len(kept):,}"
        )

    with r3:
        st.metric(
            "Records removed",
            f"{len(removed):,}"
        )

    with r4:
        st.metric(
            "Duplicate rate",
            f"{duplicate_rate:.1f}%"
        )


    st.markdown("### Duplicate review")

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
            "Decision"
        ]
    ].copy()


    st.dataframe(
        duplicate_view.head(100),
        use_container_width=True,
        hide_index=True
    )


    st.caption(
        "Duplicate Group = records that resolve to the same normalized entity. "
        "Records Found = how many records are inside that group."
    )


    st.markdown("### Download the result")

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
            "text/csv"
        )

    with d2:
        st.download_button(
            "Download removed duplicates",
            removed_csv,
            "duplicate_records.csv",
            "text/csv"
        )


# =========================================================
# METHOD NOTE
# =========================================================

st.markdown(
    """
    <div class="section-kicker">METHOD NOTE</div>
    <div class="section-title">Why process records by kecamatan?</div>

    <div class="section-copy">
        The original dataset was large, so duplicate processing
        was performed within each kecamatan rather than across the
        entire dataset at once.

        This reduced the processing workload, but it also creates
        a limitation: a duplicate recorded under different kecamatan
        could potentially be missed.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        margin-top:4rem;
        padding-top:1.3rem;
        border-top:1px solid #DDD7CD;
        color:#6D7480;
        font-family:'IBM Plex Mono', monospace;
        font-size:.74rem;
    ">
        RIZQI APRILIANES · DATA QUALITY / AUTOMATION / ANALYTICS<br>
        Synthetic public reconstruction
    </div>
    """,
    unsafe_allow_html=True
        )
