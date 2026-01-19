from langchain_google_genai import ChatGoogleGenerativeAI
from app.utils.config import GOOGLE_API_KEY

def table_agent(state):
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
        response_mime_type="application/json",
        max_output_tokens=8192
    )

    prompt = f"""
Normalize the following JSON so that:
- Every table is an array of row objects
- Keys are consistent
- Missing values are null
- Excel conversion is safe

JSON:
{state['layout_json']}
"""

    response = llm.invoke(prompt)
    content = response.content
    if isinstance(content, list):
        content = "\n".join([str(p) for p in content])
    return {"normalized_json": str(content)}
