# Kikuyu Correction Hub — Streamlit MVP

Review, correct, and approve **Gĩkũyũ** prompts for Common Voice and language datasets.

## 🚀 Deploy (Streamlit Community Cloud)
1. Create a public GitHub repo and add these files.
2. Go to https://streamlit.io/cloud, click **New app**, select your repo and `app.py`.
3. Deploy — share the URL with reviewers.

## 📂 Files
- `app.py` — Streamlit app (inline editing, approval, export)
- `requirements.txt` — minimal deps
- `data/kikuyu_spontaneous_prompts_seed.tsv` — starter prompts
- `data/kikuyu_spontaneous_prompts_review.csv` — review queue (with QA columns)
- `.streamlit/config.toml` — theming

## 🧭 Workflow
- **Review Queue**: editors fix orthography (e.g., `Warereirwo ku?`), add `dialect_note`
- Set `status=APPROVED` when 2 reviewers agree
- Export **APPROVED.tsv** for Common Voice or training

## ✍️ Notes
- Prefer modern, natural Kikuyu forms
- Keep prompts 5–12 words; avoid PII
- Use `dialect_note` to tag Nyeri/Murang'a/Kirinyaga variants

## 📜 License
This template is provided for your project. Prompts you add remain your content.