# OCR Multi-Agent Document Processing System

A **production-ready multi-agent OCR system** that converts **PDFs and images** into **structured JSON and Excel files** using **LangGraph**, **Gemini (Vision + Text)**, and **Streamlit**.

This project is designed to handle **real-world documents**, including **multi-page invoices, reports, and tables** with high accuracy.

---

## Key Features

- Multi-Agent Architecture (OCR, Processing, Export)
- Multimodal Gemini Vision (text + images together)
- Handles multi-page documents
- Strict JSON output (Excel-ready)
- Automatic table merging across pages
- Streamlit Web UI
- Optimized for free-tier API limits
- Production-grade folder structure

---

## High-Level Architecture

User Upload (PDF / Image)
- Streamlit UI
- Main Pipeline
- LangGraph Workflow
- OCR Agent
- Processor Agent (Super Agent)
- Excel Agent
- JSON + Excel Output
Multi-Agent Design

```bash
OCR → Processor → Excel
```
Although multiple agent files exist, LangGraph executes only the above flow.


The processor agent internally performs:

- layout detection

- table extraction

- JSON validation

This reduces API calls and improves performance.

Setup Instructions

## 1. Create virtual environment
```bash
python -m venv venv
```

## 2. Activate virtual environment
## Windows
```bash
venv\Scripts\activate
```

## Mac / Linux
```bash
source venv/bin/activate
```

## 3. Install dependencies
```bash
pip install -r requirements.txt
```

## 4. Add API key in .env file
```bash
GOOGLE_API_KEY=your_key_here
```


## 5. Run Streamlit application
```bash
streamlit run app/utils/streamlit_app.py
```
## 6. Expected output
- Structured JSON
- Excel (.xlsx) with metadata and tables
