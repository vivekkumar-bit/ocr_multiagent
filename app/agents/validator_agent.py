from langchain_google_genai import ChatGoogleGenerativeAI
from app.utils.config import GOOGLE_API_KEY

def validator_agent(state):
    # Gemini 1.5 Flash supports JSON mode via model_kwargs
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
        response_mime_type="application/json",
        max_output_tokens=8192
    )

    prompt = f"""
Act as a JSON repair specialist.
Your goal is to take a potentially broken JSON string and return a valid one.

RULES:
1. Fix syntax errors like trailing commas or unescaped newlines.
2. Ensure the output is a single valid JSON object.
3. Keep the keys "metadata" and "tables" as the root structure.
4. If a value contains newlines, escape them with \\n.
5. Return ONLY the JSON string. No markdown, no comments.

JSON TO REPAIR:
{state['normalized_json']}
"""

    response = llm.invoke(prompt)
    content = response.content
    if isinstance(content, list):
        content = "\n".join([str(p) for p in content])
    return {"final_json": str(content)}
