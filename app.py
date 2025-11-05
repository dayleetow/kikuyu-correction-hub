import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Kikuyu Correction Hub", page_icon="📝", layout="wide")

st.title("📝 Kikuyu Correction Hub — MVP")
st.caption("Review, correct, and approve Gĩkũyũ prompts. Export clean TSV/CSV for Common Voice or datasets.")

DATA_DIR = Path("data")
SEED_FILE = DATA_DIR / "kikuyu_spontaneous_prompts_seed.tsv"
REVIEW_FILE = DATA_DIR / "kikuyu_spontaneous_prompts_review.csv"

# Session state
if "df" not in st.session_state:
    # Load review file with QA columns; fallback to seed
    if REVIEW_FILE.exists():
        df = pd.read_csv(REVIEW_FILE)
    else:
        df = pd.read_csv(SEED_FILE, sep="\t")
        # add QA columns
        df.insert(2, "suggested_fix", "")
        df["dialect_note"] = ""
        df["status"] = "NEEDS_REVIEW"
        df["reviewer"] = ""
    st.session_state.df = df

df = st.session_state.df

with st.sidebar:
    st.header("⚙️ Controls")
    uploaded = st.file_uploader("Upload review CSV/TSV", type=["csv","tsv"])
    if uploaded is not None:
        if uploaded.name.endswith(".tsv"):
            st.session_state.df = pd.read_csv(uploaded, sep="\t")
        else:
            st.session_state.df = pd.read_csv(uploaded)
        df = st.session_state.df
        st.success(f"Loaded {len(df)} rows from {uploaded.name}")

    view = st.selectbox("View", ["Review Queue", "Approved", "All"])
    search = st.text_input("Search (Kikuyu or English)")
    dialect_filter = st.selectbox("Dialect filter", ["(any)","Nyeri","Murang'a","Kirinyaga","Diaspora"])
    topic_filter = st.selectbox("Topic filter", ["(any)"] + sorted([t for t in df["topic"].dropna().astype(str).unique()]))

    st.markdown("---")
    st.write("**Quick Add (single prompt)**")
    with st.form("add_form", clear_on_submit=True):
        new_id = st.text_input("ID", "")
        q_ki = st.text_input("Question (Gĩkũyũ)", "")
        gloss = st.text_input("English gloss", "")
        topic = st.text_input("Topic", "bio")
        secs = st.number_input("Est. seconds", min_value=3, max_value=20, value=8)
        submitted = st.form_submit_button("Add")
        if submitted:
            if new_id and q_ki:
                st.session_state.df.loc[len(st.session_state.df)] = {
                    "id": new_id,
                    "question_ki": q_ki,
                    "english_gloss": gloss,
                    "topic": topic,
                    "est_seconds": secs,
                    "suggested_fix":"",
                    "dialect_note":"",
                    "status":"NEEDS_REVIEW",
                    "reviewer":""
                }
                st.success(f"Added {new_id}")
            else:
                st.error("Please provide at least ID and Gĩkũyũ question.")

# Filtering
fdf = df.copy()
if view == "Review Queue":
    fdf = fdf[fdf["status"].fillna("NEEDS_REVIEW") == "NEEDS_REVIEW"]
elif view == "Approved":
    fdf = fdf[fdf["status"].fillna("") == "APPROVED"]

if search:
    s = search.lower()
    fdf = fdf[
        fdf["question_ki"].astype(str).str.lower().str.contains(s) |
        fdf["english_gloss"].astype(str).str.lower().str.contains(s)
    ]

if dialect_filter != "(any)":
    fdf = fdf[fdf["dialect_note"].fillna("").str.contains(dialect_filter, case=False)]

if topic_filter != "(any)":
    fdf = fdf[fdf["topic"].astype(str) == topic_filter]

st.subheader(f"Rows: {len(fdf)}")
st.caption("Click to edit fields inline. Use Approve/Reject to change status.")

# Editable table
edit_cols = ["id","question_ki","english_gloss","topic","est_seconds","suggested_fix","dialect_note","status","reviewer"]
edited = st.data_editor(
    fdf[edit_cols],
    num_rows="dynamic",
    use_container_width=True,
    key="editor"
)

# Apply edits back to main df (by id)
if st.button("💾 Save edits to session"):
    for _, row in edited.iterrows():
        idx = df.index[df["id"] == row["id"]]
        if len(idx):
            df.loc[idx, edit_cols] = row[edit_cols].values
    st.session_state.df = df
    st.success("Edits saved.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("✅ Mark selected as APPROVED"):
        ids = edited["id"].tolist()
        df.loc[df["id"].isin(ids), "status"] = "APPROVED"
        st.session_state.df = df
        st.success("Marked as APPROVED")

with col2:
    if st.button("🧹 Mark selected as NEEDS_REVIEW"):
        ids = edited["id"].tolist()
        df.loc[df["id"].isin(ids), "status"] = "NEEDS_REVIEW"
        st.session_state.df = df
        st.info("Marked as NEEDS_REVIEW")

with col3:
    # Export approved clean TSV
    appr = df[df["status"] == "APPROVED"][["id","question_ki","english_gloss","topic","est_seconds"]].copy()
    tsv = appr.to_csv(sep="\t", index=False).encode("utf-8")
    st.download_button("⬇️ Download APPROVED.tsv", tsv, file_name="approved_questions_ki.tsv", mime="text/tab-separated-values")

with col4:
    # Export full review CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download FULL_REVIEW.csv", csv, file_name="full_review_ki.csv", mime="text/csv")

st.markdown("---")
st.caption("Tip: Add dialect notes like 'Nyeri variant', 'Murang'a spelling', etc. Two approvals = ready for use.")