import os
import json
import csv
import subprocess
import re
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import extract_json_block, extract_lemmas, ROOT_DIR

# Directory containing prompt files
PROMPT_DIR = os.path.join(ROOT_DIR, "scripts/prompts")
OUTPUT_CSV = os.path.join(ROOT_DIR, "scripts/results/proposed_lemmas.csv")
OUTPUT_JSON = os.path.join(ROOT_DIR, "scripts/results/proposed_lemmas.json")
PROMPT_SCRIPT = os.path.join(ROOT_DIR, "prompt_llms.py")

# Dictionary to store extracted lemmas
lemma_data = {}


def add_lemmas(module_name, llm_model, lemmas, representation):
    """ Stores lemmas in lemma_data dictionary for structured saving. """
    if module_name not in lemma_data:
        lemma_data[module_name] = {}

    lemma_data[module_name][llm_model] = {
        "representation": representation,
        "lemmas": lemmas
    }

def save_lemmas_to_csv(csv_file):
    """ Saves the lemma dictionary to a CSV file. """
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)

    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Module Name", "LLM Model", "Lemma #", "Lemma", "Representation"])

        for module, llm_models in lemma_data.items():
            for llm_model, details in llm_models.items():
                representation = details["representation"]
                for idx, lemma in enumerate(details["lemmas"], start=1):
                    writer.writerow([module, llm_model, idx, lemma, representation])

    print(f"[INFO] Lemmas saved to {csv_file}")

def save_lemmas_to_json(json_file):
    """ Saves the lemma dictionary to a JSON file. """
    os.makedirs(os.path.dirname(json_file), exist_ok=True)

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(lemma_data, f, indent=4)

    print(f"[INFO] Lemmas saved to {json_file}")

def process_prompts(prompt_dir):
    """ Iterates over all prompt files in the directory, prompts llms and outputs returned lemmas in a . """
    
    for prompt_file in os.listdir(prompt_dir):
        if not prompt_file.endswith(".json"):  # Ensure it's a JSON prompt file
            continue
      
        prompt_path = os.path.join(prompt_dir, prompt_file)
        print(f"[INFO] Processing {prompt_path}...")

        with open(prompt_path, "r", encoding="utf-8") as f:
            json_prompt = json.load(f)

        # Run the LLM and extract JSON response
        result = subprocess.run(["python3", PROMPT_SCRIPT, prompt_path], capture_output=True, text=True)
        #print(result)
        llm_response =  result.stdout.strip()
        json_block = extract_json_block(llm_response)

        if not json_block:
            print(f"[ERROR] No valid JSON block extracted from {prompt_file}. Skipping.")
            continue

        # Extract module name, LLM model, representation
        module_name = json_prompt["module_name"]
        llm_model = json_prompt["model_name"] 
        representation = json_prompt["representation"]

        lemmas = extract_lemmas(json_block)
        if not lemmas:
            print(f"[ERROR] No lemmas found for {prompt_file}. Skipping.")
            continue
        
        add_lemmas(module_name, llm_model, lemmas, representation)

    #print(lemmas)
    # Save to CSV and JSON
    save_lemmas_to_csv(OUTPUT_CSV)
    save_lemmas_to_json(OUTPUT_JSON)

# Run the processing function
if __name__ == "__main__":
    process_prompts(PROMPT_DIR)
