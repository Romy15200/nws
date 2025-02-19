import json
import argparse
import os

def read_file(filename):
    """ Reads a file and returns its content as a string. """
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def create_json(template_file, model_file, model_name, output_json):
    """ Combines the template and Verilog file into a JSON prompt and saves it. """
    
    # Read files
    template_content = read_file(template_file)
    verilog_content = read_file(model_file)

    # Combine content
    full_prompt = f"{template_content}\n\n{verilog_content}"

    # Prepare JSON object
    data = {
        "prompt": json.dumps(full_prompt),  # Ensures JSON-safe string
        "model_name": model_name
    }

    # Save to output file
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"[INFO] JSON file '{output_json}' created successfully.")

def generate_output_filename(template_file, model_file, model_name):
    """ Generates a default output filename based on input files and model name. """
    template_name = os.path.splitext(os.path.basename(template_file))[0]  # Remove extension
    verilog_name = os.path.splitext(os.path.basename(model_file))[0]  # Remove extension
    return f"{template_name}_{verilog_name}_{model_name}.json"

def main():
    """ Parses command-line arguments and runs the script. """
    parser = argparse.ArgumentParser(description="Generate a JSON prompt file from a template and Verilog file.")
    
    parser.add_argument("template_file", help="Path to the template file.")
    parser.add_argument("model_file", help="Path to the file describing the specific model.")
    parser.add_argument("model_name", help="Name of the model.")
    parser.add_argument("-o", "--output", help="Output JSON file name (default: {template}_{verilog}_{model}.json)")

    args = parser.parse_args()
    #print(args.model_name)
    
    # Generate default output filename if not provided
    output_file = args.output if args.output else generate_output_filename(args.template_file, args.model_file, args.model_name)
    #print(output_file)
    
    create_json(args.template_file, args.model_file, args.model_name, output_file)

if __name__ == "__main__":
    main()
