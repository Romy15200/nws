import os
import subprocess
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import ROOT_DIR


# directory containing the verilog modules
directory_with_modules = os.path.join(ROOT_DIR, "hard_properties")  
template_file = os.path.join(ROOT_DIR, "templates/verilog.txt")
# LLM models to be prompted
#models = ["gpt-4o", "anthropic.claude-v2:1", "meta-llama/Llama-3.1-8B-Instruct"]  # 
models = ["deepseek-r1"]

script_path = os.path.join(ROOT_DIR, "scripts/create_json_prompt.py" )


output_directory = os.path.join(ROOT_DIR, "scripts/prompts")
print(output_directory)
os.makedirs(output_directory, exist_ok=True)


for filename in os.listdir(directory_with_modules):
    module_file = os.path.join(directory_with_modules, filename)
    
    # Ensure it's a file (not a directory)
    if os.path.isfile(module_file):
        
        # Iterate over each model name
        for model in models:
            print(f"Processing {filename} with model {model}...")
            
            command = ["python3", script_path, "--template_file", template_file, "--module_file", module_file, "--model_name", 
                       model, "--output_dir", output_directory]
            
            print(subprocess.run(command, check=True)) # generates JSON file
