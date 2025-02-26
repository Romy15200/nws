import json
import argparse
import os

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

def main():
    """ Parses command-line arguments and runs the script. """
    parser = argparse.ArgumentParser(description="Generate a JSON prompt file from a template and module description file.")
    
    parser.add_argument("--template_file", help="Path to the template file.")
    parser.add_argument("--module_file", help="Path to the file describing the specific module.")
    parser.add_argument("--model_name", help="Name of the llm model to be prompted.")
    parser.add_argument("-o", "--output", help="Output JSON file name (default: {template}_{verilog}_{model}.json)")
    parser.add_argument("--output_dir", help="where to save the JSON files. Default: current working directory")

    args = parser.parse_args()
    #print(args.model_name)
    
    # Generate default output filename if not provided
    output_file = args.output if args.output else generate_output_filename(args.template_file, args.module_file, args.model_name)
    if args.output_dir:
        output_file = os.path.join(args.output_dir, output_file)
    #print(output_file)
    
    create_json(args.template_file, args.module_file, args.model_name, output_file)

if __name__ == "__main__":
    main()
