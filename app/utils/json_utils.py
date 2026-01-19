import re
import json

def extract_json(text: any) -> str:
    """
    Extracts the JSON string from a text that might contain markdown code blocks or other noise.
    """
    if isinstance(text, list):
        parts = []
        for part in text:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and 'text' in part:
                parts.append(part['text'])
        text = "\n".join(parts)
    
    if not isinstance(text, str):
        text = str(text)

    # 1. Remove markdown indicators
    text = re.sub(r'```(?:json)?', '', text)
    text = text.replace('```', '')
    
    # 2. Handle potential Python dict string wrapper (e.g., {'type': 'text', 'text': '...'})
    # This happens if response.content is stringified incorrectly
    dict_wrapper_pattern = r"\{'type':\s*'text',\s*'text':\s*['\"](\{.*\}|\[.*\])['\"]\}"
    match = re.search(dict_wrapper_pattern, text, re.DOTALL)
    if match:
        text = match.group(1).replace("\\n", "\n").replace("\\'", "'").replace('\\"', '"')

    # 3. Find outermost JSON structure
    start_brace = text.find('{')
    start_bracket = text.find('[')
    
    if start_brace == -1 and start_bracket == -1:
        return text.strip()
        
    if start_brace != -1 and (start_bracket == -1 or start_brace < start_bracket):
        start = start_brace
        # Try to find the matching closing brace instead of just the last one
        # but for simple cases, rfind is often enough. 
        # However, if it's wrapped in a dict, rfind might find the outer one.
        # Let's count braces to be safer
        brace_count = 0
        end = -1
        for i in range(start, len(text)):
            if text[i] == '{':
                brace_count += 1
            elif text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end = i
                    break
        if end == -1: end = text.rfind('}')
    else:
        start = start_bracket
        bracket_count = 0
        end = -1
        for i in range(start, len(text)):
            if text[i] == '[':
                bracket_count += 1
            elif text[i] == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    end = i
                    break
        if end == -1: end = text.rfind(']')
        
    if start != -1 and end != -1 and end > start:
        return text[start:end+1].strip()
    
    return text.strip()

def repair_json(json_str: str) -> str:
    """
    Extremely robust repair for common LLM JSON errors.
    """
    if not json_str:
        return "{}"

    # 1. Basic cleaning
    json_str = json_str.strip()
    
    # 2. Fix missing commas between key-value pairs on the same line
    # Match: "value" "key": or 123 "key": or true "key":
    # This is a common LLM error
    json_str = re.sub(r'("|\d|true|false|null|])\s*\n?\s*(")', r'\1, \2', json_str)
    
    # 3. Handle unescaped internal newlines
    # Join lines that don't end in structural characters
    lines = json_str.splitlines()
    repaired_lines = []
    for i, line in enumerate(lines):
        line = line.rstrip()
        if not line: continue
        
        # If the line ends with a comma/brace/bracket/colon, it's probably fine
        if line.endswith((',', '{', '[', ':', '}', ']')):
            repaired_lines.append(line)
        else:
            # Check for missing comma: if next line starts with "key":
            if i < len(lines) - 1:
                next_line = lines[i+1].strip()
                if next_line.startswith('"') and ':' in next_line:
                    line += ","
                else:
                    line += " \\n " # Assume it's a split string
            repaired_lines.append(line)
            
    json_str = "\n".join(repaired_lines).strip()

    # 4. Final safety: Fix trailing commas
    json_str = re.sub(r',\s*([\]\}])', r'\1', json_str)

    # 5. Handle truncation: balance braces
    open_braces = json_str.count('{')
    close_braces = json_str.count('}')
    open_brackets = json_str.count('[')
    close_brackets = json_str.count(']')
    
    if open_brackets > close_brackets:
        json_str += ']' * (open_brackets - close_brackets)
    if open_braces > close_braces:
        json_str += '}' * (open_braces - close_braces)
        
    return json_str

def safe_json_loads(text):
    """
    Safely loads JSON with multiple fallback layers and detailed logging.
    """
    cleaned = extract_json(text)
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        try:
            repaired = repair_json(cleaned)
            return json.loads(repaired)
        except json.JSONDecodeError as e:
            # Last ditch: try replacing single quotes if it looks like a dict
            try:
                if "'" in cleaned:
                    fixed_quotes = cleaned.replace("'", '"')
                    return json.loads(repair_json(fixed_quotes))
            except:
                pass
                
            print(f"JSON REPAIR FAILED: {e}")
            print(f"Attempted Repair Content: {cleaned[:200]}...")
            
            # Emergency fallback: construct a basic object so the app doesn't crash
            return {
                "metadata": {"error": "JSON Parse Failure", "raw_hint": cleaned[:100]},
                "tables": []
            }
