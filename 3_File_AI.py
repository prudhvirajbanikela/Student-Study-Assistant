# ============================================================
# AI FILE ANALYZER + CHAT ASSISTANT
# ============================================================

import os
import json
import fitz
import yaml
import pandas as pd
import streamlit as st
import plotly.express as px
import xml.etree.ElementTree as ET

from pathlib import Path
from docx import Document
from groq import Groq
from PIL import Image
import pytesseract
import io

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI File Analyzer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI File Analyzer + Chat Assistant")

# ============================================================
# GROQ CONFIG
# ============================================================

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "file_text" not in st.session_state:
    st.session_state.file_text = ""

if "df" not in st.session_state:
    st.session_state.df = None

if "file_name" not in st.session_state:
    st.session_state.file_name = ""

# ============================================================
# OCR HELPER — extracts text from scanned PDF using pytesseract
# ============================================================

def ocr_pdf(uploaded_file) -> str:
    """
    Convert each page of a scanned PDF to an image,
    then run Tesseract OCR to extract text.
    """

    uploaded_file.seek(0)
    pdf_bytes = uploaded_file.read()

    pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
    all_text = []

    for i, page in enumerate(pdf):

        # Render page to image at 300 DPI
        mat = fitz.Matrix(300 / 72, 300 / 72)
        pix = page.get_pixmap(matrix=mat)

        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))

        # 🔥 IMPORTANT FIX (add safety here)
        try:
            page_text = pytesseract.image_to_string(img, lang="eng")
        except Exception as e:
            page_text = f"[OCR ERROR on page {i+1}: {e}]"

        if page_text.strip():
            all_text.append(f"--- Page {i+1} ---\n{page_text.strip()}")

    pdf.close()
    return "\n\n".join(all_text)

# ============================================================
# FILE READER
# ============================================================

def read_file(uploaded_file):

    ext = Path(uploaded_file.name).suffix.lower()

    try:

        uploaded_file.seek(0)

        # CSV
        if ext == ".csv":

            df = pd.read_csv(uploaded_file)

            text = (
                f"[CSV FILE: {uploaded_file.name}]\n"
                f"Rows: {len(df)} | Columns: {len(df.columns)}\n"
                f"Columns: {', '.join(df.columns.tolist())}\n\n"
                + df.head(500).to_string()
            )

            return text, df

        # Excel
        elif ext in [".xlsx", ".xls"]:

            df = pd.read_excel(uploaded_file)

            text = (
                f"[EXCEL FILE: {uploaded_file.name}]\n"
                f"Rows: {len(df)} | Columns: {len(df.columns)}\n"
                f"Columns: {', '.join(df.columns.tolist())}\n\n"
                + df.head(500).to_string()
            )

            return text, df

        # PDF — text extraction first, OCR fallback for scanned PDFs
        elif ext == ".pdf":

            uploaded_file.seek(0)

            pdf = fitz.open(
                stream=uploaded_file.read(),
                filetype="pdf"
            )

            pages = []

            for i, page in enumerate(pdf):
                page_text = page.get_text().strip()
                if page_text:
                    pages.append(f"--- Page {i+1} ---\n{page_text}")

            pdf.close()

            text = "\n\n".join(pages).strip()

            # ── SCANNED PDF: fall back to OCR ──────────────────
            if not text:
                st.info(
                    "🔍 Scanned PDF detected — running OCR "
                    "(this may take 30–60 seconds)..."
                )
                with st.spinner("Running OCR on scanned pages..."):
                    text = ocr_pdf(uploaded_file)

                if not text.strip():
                    return (
                        f"[PDF FILE: {uploaded_file.name}]\n"
                        "[OCR found no readable text. "
                        "Try a higher-quality scan.]",
                        None
                    )

                return (
                    f"[SCANNED PDF — OCR EXTRACTED: {uploaded_file.name}]\n\n"
                    + text,
                    None
                )

            return f"[PDF FILE: {uploaded_file.name}]\n\n{text}", None

        # DOCX
        elif ext == ".docx":

            uploaded_file.seek(0)

            doc = Document(uploaded_file)

            text = "\n".join(
                p.text for p in doc.paragraphs if p.text.strip()
            )

            return f"[WORD FILE: {uploaded_file.name}]\n\n{text}", None

        # TXT
        elif ext == ".txt":

            uploaded_file.seek(0)

            text = uploaded_file.read().decode(
                "utf-8",
                errors="ignore"
            )

            return f"[TEXT FILE: {uploaded_file.name}]\n\n{text}", None

        # JSON
        elif ext == ".json":

            uploaded_file.seek(0)

            data = json.load(uploaded_file)

            return (
                f"[JSON FILE: {uploaded_file.name}]\n\n"
                + json.dumps(data, indent=2),
                None
            )

        # XML
        elif ext == ".xml":

            uploaded_file.seek(0)

            tree = ET.parse(uploaded_file)
            root = tree.getroot()

            return (
                f"[XML FILE: {uploaded_file.name}]\n\n"
                + ET.tostring(root, encoding="unicode"),
                None
            )

        # YAML
        elif ext in [".yaml", ".yml"]:

            uploaded_file.seek(0)

            data = yaml.safe_load(uploaded_file)

            return (
                f"[YAML FILE: {uploaded_file.name}]\n\n"
                + yaml.dump(data, allow_unicode=True),
                None
            )

        return "Unsupported file type", None

    except Exception as e:

        return f"Error reading file: {e}", None

# ============================================================
# FILE UPLOADER
# ============================================================

uploaded_file = st.file_uploader(
    "Upload Any File",
    type=[
        "csv",
        "xlsx",
        "xls",
        "pdf",
        "docx",
        "txt",
        "json",
        "xml",
        "yaml",
        "yml"
    ]
)

if uploaded_file:

    if uploaded_file.name != st.session_state.file_name:

        with st.spinner(f"📖 Reading {uploaded_file.name}..."):
            uploaded_file.seek(0)
            text, df = read_file(uploaded_file)

        st.session_state.file_text = text
        st.session_state.df = df
        st.session_state.file_name = uploaded_file.name
        st.session_state.messages = []

        st.success(
            f"✅ {uploaded_file.name} loaded — {len(text):,} characters extracted"
        )

if st.session_state.file_text:

    with st.expander("🔍 Verify: content sent to AI", expanded=False):
        st.text(st.session_state.file_text[:3000])
        st.caption(
            f"Total: {len(st.session_state.file_text):,} chars  |  "
            f"Sent to AI: up to 50,000 chars"
        )

# ============================================================
# DATASET ANALYTICS
# ============================================================

if st.session_state.df is not None:

    st.subheader("📊 Dataset Analytics")

    df = st.session_state.df

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Rows",
        len(df)
    )

    c2.metric(
        "Columns",
        len(df.columns)
    )

    c3.metric(
        "Missing Values",
        int(df.isnull().sum().sum())
    )

    st.dataframe(
        df.head(100),
        use_container_width=True
    )

    st.subheader("📈 Statistics")

    st.dataframe(
        df.describe(
            include="all"
        ),
        use_container_width=True
    )

    num_cols = df.select_dtypes(
        include="number"
    ).columns.tolist()

    if len(num_cols) > 0:

        selected_col = st.selectbox(
            "Select Numeric Column",
            num_cols
        )

        fig = px.histogram(
            df,
            x=selected_col
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚙️ Controls")

    if st.button("🧹 Clear Chat"):

        st.session_state.messages = []
        st.rerun()

    if st.button("📂 Remove File"):

        st.session_state.file_text = ""
        st.session_state.df = None
        st.session_state.file_name = ""

        st.rerun()

    if st.button("🔥 Reset Everything"):

        st.session_state.clear()
        st.rerun()

    st.divider()

    st.write(
        f"💬 Messages: {len(st.session_state.messages)}"
    )

    if st.session_state.file_name:

        st.write(
            f"📂 File: {st.session_state.file_name}"
        )

        st.write(
            f"📝 {len(st.session_state.file_text):,} chars loaded"
        )

# ============================================================
# PROMPT BUILDER
# ============================================================

def build_prompt(question):

    history = "\n".join([

        f"{m['role']} : {m['content']}"

        for m in st.session_state.messages[-10:]

    ])

    file_content = st.session_state.file_text[:50000]

    if file_content.strip():
        file_status = (
            f"LOADED ✅ — {st.session_state.file_name} "
            f"({len(st.session_state.file_text):,} characters extracted)"
        )
    else:
        file_status = "NOT UPLOADED ❌ — answer from general knowledge only"

    return f"""
You are an advanced AI Assistant.

FILE STATUS: {file_status}

IMPORTANT RULES:

1. The FILE CONTENT below is REAL extracted text. Read it carefully.
2. NEVER say "I don't have access to the file" — it is right here.
3. NEVER ask the user to upload again.
4. NEVER give a generic response — be specific to THIS exact file.
5. Analyze uploaded file deeply.
6. Use chat history for context.
7. Reply in same language as user.
8. Use bullet points.
9. Give professional answer.
10. If PDF → summarize what is ACTUALLY written in it.
11. If dataset → analyze the actual columns and values.

FILE CONTENT:

{file_content if file_content.strip() else "[No file uploaded]"}

CHAT HISTORY:

{history if history.strip() else "[No previous messages]"}

QUESTION:

{question}
"""

# ============================================================
# ASK AI
# ============================================================

def ask_ai(prompt):

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.4,
        max_tokens=2048

    )

    return response.choices[0].message.content

# ============================================================
# QUICK SUMMARY BUTTON
# ============================================================

if st.session_state.file_text:

    if st.button("📑 Summarize Uploaded File"):

        with st.spinner("Generating Summary..."):

            summary = ask_ai(

                f"""
Summarize this file completely and specifically.
Give the main topics, key points, and important details.
The content is RIGHT BELOW — do not say you cannot access it.
Be specific to this exact file content.

FILE CONTENT:
{st.session_state.file_text[:50000]}
"""
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": summary
            }
        )

        st.rerun()

# ============================================================
# CHAT HISTORY DISPLAY
# ============================================================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask anything about your file..."
)

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    prompt = build_prompt(question)

    try:

        answer = ask_ai(prompt)

    except Exception as e:

        answer = f"❌ Error: {e}"

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    with st.chat_message("assistant"):

        st.markdown(answer)
