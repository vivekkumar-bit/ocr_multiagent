from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.utils.config import GOOGLE_API_KEY
import base64
import io

def processor_agent(state):
    """
    Multimodal Super Agent: Uses Gemini Vision to process multiple pages at once.
    Highly accurate for multi-page documents (10-20+ pages).
    """
    # Increased max_output_tokens to handle large tables (10-20 pages)
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest", 
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
        response_mime_type="application/json",
        max_output_tokens=16384 
    )

    prompt_text = """
Act as an expert Document Extraction & JSON Specialist.
You are provided with images of document pages. Your task is to extract data from ALL pages into a single structured JSON.

STYLE RULES:
1. Use snake_case (underscores) for all keys (e.g., "invoice_number", "sender_name").
2. Ensure values are trimmed of extra whitespace.

STRICT SYNTAX RULES:
1. Every key and value MUST be enclosed in double quotes.
2. Every field in an object MUST be separated by a comma.
3. Every element in an array MUST be separated by a comma.
4. Internal newlines in values MUST be escaped as \\n.
5. NO trailing commas.
6. NO extra text before or after the JSON object.

EXTRACTION GOALS:
1. Extract metadata (Names, Dates, ID numbers, Addresses, Totals) into the "metadata" object.
2. Extract ALL tables. Merge tables if they span across multiple pages (e.g., one long stock list).
3. IMPORTANT: You MUST extract every single row from every single page. Do NOT skip or summarize data.
4. Each table must be an object with a "rows" array. Each row is an object of consistent key-value pairs.
5. If data is missing, use null.

JSON STRUCTURE:
{
  "metadata": { "field_name": "Value", ... },
  "tables": [
    { "rows": [ { "col_name": "Val", "col_name_2": "Val" }, ... ] }
  ]
}
"""

    # Prepare multimodal content
    content = [{"type": "text", "text": prompt_text}]
    
    # Add images to content
    images = state.get("images", [])
    print(f"DEBUG: Processing {len(images)} pages with Gemini Vision...")
    
    for i, img in enumerate(images):
        # Convert PIL to base64
        # JPEG doesn't support RGBA or other modes with transparency, so always convert to RGB
        img = img.convert('RGB')
        
        # Optional: Resize very large images to keep payload manageable for 20+ pages
        if img.width > 2000 or img.height > 2000:
            img.thumbnail((2000, 2000))
            
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=85) # Slight quality reduction to save bandwidth
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        content.append({
            "type": "image_url",
            "image_url": f"data:image/jpeg;base64,{img_str}"
        })

    # Fallback: if no images, use raw_text if available
    if not images and state.get("raw_text"):
        content.append({"type": "text", "text": f"\nOCR TEXT TO PROCESS:\n{state['raw_text']}"})

    message = HumanMessage(content=content)
    
    print("DEBUG: Sending request to Gemini...")
    response = llm.invoke([message])
    content_out = response.content
    print(f"DEBUG: Received response from Gemini ({len(content_out)} chars)")
    
    # Handle LangChain/Gemini content parts
    if isinstance(content_out, list):
        text_parts = []
        for part in content_out:
            if isinstance(part, str):
                text_parts.append(part)
            elif isinstance(part, dict) and 'text' in part:
                text_parts.append(part['text'])
        content_out = "".join(text_parts)
        
    return {
        "final_json": content_out,
        "layout_json": content_out,
        "normalized_json": content_out
    }
