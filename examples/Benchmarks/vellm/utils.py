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


def read_file(filename):
    """ Reads a file and returns its content as a string. """
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def create_json(template_file, module_file, model_name, output_json):
    """ Combines the template and Verilog file into a JSON prompt and saves it. """
    
    # Read files
    template_content = read_file(template_file)
    verilog_content = read_file(module_file)
    module_file_base_name = os.path.splitext(os.path.basename(module_file))[0]
    template_file_base_name = os.path.splitext(os.path.basename(template_file))[0]
    # Combine content
    full_prompt = f"{template_content}\n\n{verilog_content}"

    # Prepare JSON object
    data = {
        "prompt": json.dumps(full_prompt),  # Ensures JSON-safe string
        "model_name": model_name,
        "module_name": module_file_base_name,
        "representation": template_file_base_name
        }

    # Save to output file
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"[INFO] JSON file '{output_json}' created successfully.")

def generate_output_filename(template_file, module_file, model_name):
    """ Generates a default output filename based on input files and model name. """
    template_name = os.path.splitext(os.path.basename(template_file))[0]  # remove extension
    module_name = os.path.splitext(os.path.basename(module_file))[0]  # remove extension
    clean_model_name =  model_name.split("/")[-1] # in case model name can be interpreted as a path
    return f"{template_name}_{module_name}_{clean_model_name}.json"