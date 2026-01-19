from app.utils.json_utils import safe_json_loads

test_input = "{'type': 'text', 'text': '{\\n  \"metadata\": {\\n    \"Sender_Name\": \"EarnAxis\",\\n    \"Sender_Address\": \"San Francisco, CA 94102\"\\n  }\\n}'}"

print("Testing with wrapped dict string:")
result = safe_json_loads(test_input)
print(result)

test_input_2 = "```json\n{\n  \"metadata\": {\n    \"invoice_number\": \"123\"\n  }\n}\n```"
print("\nTesting with markdown:")
result_2 = safe_json_loads(test_input_2)
print(result_2)
