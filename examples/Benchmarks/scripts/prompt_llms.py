import boto3
from openai import OpenAI
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import json
from diskcache import Cache
import hashlib
import argparse
import os

def call_llama(prompt, model_name="meta-llama/Llama-3.1-8B-Instruct", temperature=0.7, max_tokens=256):
    """
    Prompts a Llama model using the Transformers library.

    Args:
        prompt (str): The input prompt for the model.
        model_name (str): The Hugging Face model identifier.
        temperature (float): Sampling temperature for randomness.
        max_tokens (int): Maximum number of tokens to generate.

    Returns:
        str: The generated response.
    """
    # Load model and tokenizer
    #print(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Encode the input prompt
    inputs = tokenizer(prompt, return_tensors="pt")

    # Generate output with specified parameters
    outputs = model.generate(
        inputs.input_ids,
        max_new_tokens=max_tokens,
        temperature=temperature,
        do_sample=True,
        top_k=50,  # Optional: Top-k sampling for diversity
    )

    # Decode and return the response
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def call_bedrock(prompt, model_name, temperature, max_tokens=256):
    # Initialize Bedrock client
    client = boto3.client(
        service_name='bedrock-runtime',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name='us-east-1'
    )

    
    payload = {
        "prompt": prompt,
        "max_tokens_to_sample": max_tokens,
        "temperature": temperature
    }


    # Call Bedrock API
    response = client.invoke_model(
        modelId=model_name,  
        contentType='application/json',
        accept='application/json',
        body=json.dumps(payload)
    )

    # Parse and return result
    result = json.loads(response.get('body').read())
    return result.get('completion')


def call_gpt(prompt, model_name, temperature, max_tokens=256):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))  

    messages = [
        {"role": "assistant", "content": ""},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    #print(response)
    response_text = response.choices[0].message.content
    return response_text



def get_from_cache_or_prompt(prompt, model_name, temperature, max_tokens, call_func):
    # Create a unique cache key
    cache_key = hashlib.sha256(f"{prompt}-{model_name}-{temperature}-{max_tokens}".encode()).hexdigest()

    if cache_key in cache:
        # Return cached response
        print("Cache hit")
        return cache[cache_key]
    else:
        # Call LLM and cache the response
        print("Cache miss")
        response = call_func(prompt, model_name, temperature, max_tokens)
        cache[cache_key] = response
        return response

def query_llm(prompt, model_name, temperature=0.7, max_tokens=256, llama_model_path=None):
    #print(model_name)
    if model_name.startswith("meta-llama"):
        # Use local Llama
        return get_from_cache_or_prompt(prompt, model_name, temperature, max_tokens, call_llama)
                                       # lambda p, m, t, mt: call_llama(p, llama_model_path, t, mt))
    elif model_name.startswith("gpt"):
        return get_from_cache_or_prompt(prompt, model_name, temperature, max_tokens, call_gpt)
    else:
        # Use Bedrock
        return get_from_cache_or_prompt(prompt, model_name, temperature, max_tokens, call_bedrock)


if __name__ == "__main__":
    
    # Initialize cache
    cache = Cache('./cache')

    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str, help="Path to the JSON file containing the prompt, model and parameter specifications.")
    args = parser.parse_args()

    
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    region_name = os.getenv('REGION_NAME')

    # Load the configuration from the JSON file
    with open(args.config_file, 'r') as f:
        params = json.load(f)

    # if 'prompt' not in params:
    #     raise ValueError("The JSON configuration file must include a 'prompt' field.")

    # Gets the response from the cache or by prompting the LLM
    response = query_llm(**params)

    # Print the response
    print("LLM Response: ", response)
    
    cache.close()
   
