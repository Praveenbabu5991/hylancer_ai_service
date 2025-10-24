# app/utils/parser.py - Includes a helper to safely parse LLM responses to JSON.

import json
from typing import Any, Dict

def parse_llm_response_to_json(response_text: str) -> Dict[str, Any]:
    """
    Safely parses an LLM response string into a JSON object.
    Handles cases where the LLM might return extra text around the JSON.
    """
    try:
        # Attempt to find the JSON part of the string
        start_index = response_text.find('{')
        end_index = response_text.rfind('}')

        if start_index != -1 and end_index != -1 and start_index < end_index:
            json_string = response_text[start_index : end_index + 1]
            return json.loads(json_string)
        else:
            # If no clear JSON object is found, try parsing the whole thing
            return json.loads(response_text)
    except json.JSONDecodeError:
        # Fallback if parsing fails
        print(f"Warning: Could not parse LLM response to JSON. Response: {response_text}")
        return {"raw_response": response_text, "error": "JSON parsing failed"}
    except Exception as e:
        print(f"An unexpected error occurred during JSON parsing: {e}. Response: {response_text}")
        return {"raw_response": response_text, "error": f"Unexpected error: {str(e)}"}
