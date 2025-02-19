import json
import subprocess
import re
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
 # Run the prompt_llms script
def prompt_llm(prompt_file):

     result = subprocess.run(["python3", "prompt_llms.py", prompt_file], capture_output=True, text=True)
     #print(result)
     return result.stdout.strip()

# Extract the JSON block from the LLM response
def extract_json_block(llm_output):
    """ Extracts the JSON content from within triple backticks (`JSON ...`). """
    match = re.search(r"```JSON\s*(\{.*?\})\s*```", llm_output, re.DOTALL | re.IGNORECASE)
    if match:
        json_text = match.group(1)
        try:
            return json.loads(json_text)  # Convert to Python dictionary
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse JSON: {e}")
            return None
    else:
        print("[ERROR] No JSON block found in LLM output.")
        return None

# Extract lemmas from parsed JSON
def extract_lemmas(json_data):
    """ Parses lemmas from JSON output. """
    try:
        return [list(lemma.values())[0] for lemma in json_data["lemmas"]]
    except (KeyError, TypeError, IndexError) as e:
        print(f"[ERROR] Invalid JSON structure: {e}")
        return []
