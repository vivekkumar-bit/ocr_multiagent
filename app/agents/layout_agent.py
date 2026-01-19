from langchain_google_genai import ChatGoogleGenerativeAI
from app.utils.config import GOOGLE_API_KEY

def layout_agent(state):
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
        response_mime_type="application/json",
        max_output_tokens=8192
    )

    prompt = f"""
You are a document understanding agent.

From the OCR text below:
1. Detect sections (header, customer info, tables, totals).
2. Identify all tables (any number).
3. Output a JSON with:
   - metadata (key-value pairs)
   - tables (list of tables with rows)

Return ONLY valid JSON.

OCR TEXT:
{state['raw_text']}
"""

    response = llm.invoke(prompt)
    content = response.content
    if isinstance(content, list):
        content = "\n".join([str(p) for p in content])
    return {"layout_json": str(content)}
