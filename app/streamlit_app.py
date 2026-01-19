import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app.main import run_pipeline

st.set_page_config("OCR Multi-Agent", layout="wide")
st.title("Multi-Agent AI")

file = st.file_uploader("upload file here", type=["pdf", "png", "jpg", "jpeg"])

@st.cache_data(show_spinner=False)
def cached_run_pipeline(file_bytes, file_type):
    return run_pipeline(file_bytes, file_type)

if file:
    file_type = "pdf" if file.name.endswith(".pdf") else "image"

    with st.spinner("Processing using Multi-Agent AI..."):
        # We use the cached version to avoid burning API quota on UI refreshes
        result = cached_run_pipeline(file.read(), file_type)

    st.success("Done ")

    st.subheader("JSON Output")
    st.code(result["final_json"], language="json")

    st.download_button(
        " Download Excel",
        data=result["excel_file"],
        file_name="output.xlsx"
    )
