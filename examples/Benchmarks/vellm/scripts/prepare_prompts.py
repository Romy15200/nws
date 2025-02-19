import os
import subprocess

# directory containing the verilog modules
directory_with_modules = "/home/romy.peled/vellm/nws/examples/Benchmarks/vellm/hard_properties"  
template_file = "/home/romy.peled/vellm/nws/examples/Benchmarks/vellm/templates/verilog.txt"

# LLM models to be prompted
models = ["gpt-4o", "anthropic.claude-v2:1", "meta-llama/Llama-3.1-8B-Instruct"]  # 


script_path = "/home/romy.peled/vellm/nws/examples/Benchmarks/vellm/scripts/prepare_json_prompt.py" 


output_directory = "/home/romy.peled/vellm/nws/examples/Benchmarks/vellm/scripts/prompts"
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
