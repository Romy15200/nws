import json
import subprocess
import re
import shutil
import os

ebmc_executable = "/home/romy.peled/hw-cbmc/src/ebmc/ebmc" # Path to the EBMC executable

# Run the prompt_llms script
def call_llm(prompt_file):
    """ Calls the LLM to generate lemmas using prompt_llms.py. """
    result = subprocess.run(["python3", "prompt_llms.py", prompt_file], capture_output=True, text=True)
    #print(result)
    return result.stdout.strip()

# Extract the JSON block from the LLM response
def extract_json_block(llm_output):
    """ Extracts the JSON content from within triple backticks (`JSON ...`). """
    match = re.search(r"```JSON\s*(\{.*?\})\s*```", llm_output, re.DOTALL)
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

# Insert a lemma before "endmodule" in the SystemVerilog file
def insert_lemma_to_sv(original_file, lemma, output_file):
    """ Inserts a lemma before the 'endmodule' statement in a SystemVerilog file. """
    with open(original_file, "r") as f:
        lines = f.readlines()
    
    # Find "endmodule" and insert the lemma before it
    for i in range(len(lines) - 1, -1, -1):
        if re.match(r"^\s*endmodule\s*$", lines[i]):
            lines.insert(i, f"{lemma}\n")
            break
    
    with open(output_file, "w") as f:
        f.writelines(lines)


# Check whether proposed lemma is correct
def check_correctness(sv_file, lemma, idx):

    # Correctness Test: Modify Verilog with 'assert' version
    base_name_no_ext = os.path.splitext(os.path.basename(sv_file))[0]
    correctness_sv = f"temp_sv/{base_name_no_ext}_correctness_{idx+1}.sv"
    print(correctness_sv)

    with open(sv_file, "r") as f:
        lines = f.readlines()
    
    for i in range(len(lines)):
        if "assert property" in lines[i]:  # Find the first assert
            lines[i] = f"{lemma.replace('assume property', 'assert property', 1)}\n"  # Replace with the proposed lemma
            break  
    
    os.makedirs(os.path.dirname(correctness_sv), exist_ok=True)

    with open(correctness_sv, "w") as f:
        f.writelines(lines)


    print(f"[INFO] Running EBMC for correctness test on {correctness_sv}...")
    correctness_output = run_ebmc(correctness_sv)

# Check whether when proposed lemma is assumed, hard property is verified
def check_useful(sv_file, lemma):
    pass

# Run EBMC and return its result
def run_ebmc(sv_file):
    """ Runs EBMC on a given SystemVerilog file and returns the result. """
    result = subprocess.run([ebmc_executable, sv_file], capture_output=True, text=True)
    print(result)
    return result.stdout

# Main execution
def main():

   
    prompt_file = "verilog_gray_11-p3_gpt-4o.json"
    sv_file ="../hard_properties/gray_11-p3.sv"
    print("[INFO] Running LLM to generate lemmas...")
    llm_response = call_llm(prompt_file)
    #print(llm_response)
    
    print("[INFO] Extracting JSON block from LLM response...")
    json_data = extract_json_block(llm_response)

    if not json_data:
        print("[ERROR] JSON extraction failed. Exiting.")
        return

    #print(json_data)

    print("[INFO] Extracting lemmas...")
    lemmas = extract_lemmas(json_data)

    if not lemmas:
        print("[ERROR] No lemmas extracted. Exiting.")
        return

    print(lemmas)

    #os.makedirs("ebmc_results", exist_ok=True)

    for idx, lemma in enumerate(lemmas):
        print(f"[INFO] Evaluating Lemma {idx+1}: {lemma}")
        
        print(check_correctness(sv_file, lemma, idx))

    #     print(f"[INFO] Running EBMC on {modified_sv}...")
    #     ebmc_output = run_ebmc(modified_sv)

    #     result_file = f"ebmc_results/result_lemma_{idx+1}.txt"
    #     with open(result_file, "w") as f:
    #         f.write(ebmc_output)

    #     print(f"[INFO] EBMC result saved in {result_file}")

    # print("[INFO] Finished processing all lemmas.")

   

if __name__ == "__main__":
    main()
