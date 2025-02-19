import boto3
from openai import OpenAI
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import json
from diskcache import Cache
import hashlib
import random
import torch
import ollama
import argparse
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
import os
import requests


class LLMBase(ABC):
    def __init__(self, model_name: str, cache_dir: str = "./llm_cache"):
        self.model_name = model_name
        self.cache = Cache(cache_dir)

    def _hash_query(self, prompt: str) -> str:
        """Generate a hash for the prompt and model name to use as a cache key."""
        #return hashlib.sha256(prompt.encode()).hexdigest()
        return hashlib.sha256(f"{prompt}-{self.model_name}".encode()).hexdigest()
    
    def _sample_from_responses(self, responses: List[Tuple[str, float]], temperature: float) -> Tuple[str, float]:
        """Sample a response based on temperature with a fixed random seed."""
        random.seed(42)  
        if temperature == 0:
            return responses[0]  # deterministic: always return the first response
        return random.choices(responses, k=1)[0]

    def get_response(self, prompt: str, temperature: float) -> Tuple[str, float]:
        """Check cache or generate new responses."""
        query_hash = self._hash_query(prompt)
        
        if query_hash in self.cache:
            print("Cache hit")
            responses = self.cache[query_hash]
        else:
            print("Cache miss")
            responses = self._generate_responses(prompt, num_samples=5)
            self.cache[query_hash] = responses  # store in cache
        
        return self._sample_from_responses(responses, temperature)

    @abstractmethod
    def _generate_responses(self, prompt: str, num_samples: int = 5, temperature=0.7) -> List[Tuple[str, float]]:
        """Generate multiple responses along with their probabilities for a prompt."""
        pass


class Llama(LLMBase):
    def __init__(self, model_name: str, cache_dir: str = "./llm_cache"):
        super().__init__(model_name, cache_dir)
        self.device =  0 if torch.cuda.is_available() else -1
        self.generator = pipeline("text-generation", model=model_name, device=self.device)
       

    def _generate_responses(self, prompt: str, num_samples: int, temperature = 0.7) -> List[Tuple[str, float]]:
        responses = []
        # for _ in range(num_samples):
        #     response = self.generator(prompt, num_return_sequences=1, return_full_text=False)
        #     responses.append((response[0]["generated_text"], 1.0))  # Probability info not available
        responses = self.generator(prompt, num_return_sequences=num_samples, return_full_text=False, max_new_tokens = 4096)
        return responses


class Claude(LLMBase):
    def __init__(self, model_name: str, cache_dir: str = "./llm_cache"):
        super().__init__(model_name, cache_dir)
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')     
        self.region_name = os.getenv('AWS_REGION_NAME')
        
        self.client = boto3.client("bedrock-runtime", aws_access_key_id=self.aws_access_key_id, 
                                   aws_secret_access_key=self.aws_secret_access_key, region_name=self.region_name)

    def _generate_responses(self, prompt: str, num_samples: int, temperature = 0.7) -> List[Tuple[str, float]]:
        responses = []
        for _ in range(num_samples):
            response = self.client.invoke_model(modelId=self.model_name, contentType='application/json', 
                                                accept='application/json', body=json.dumps({"prompt": prompt, "max_tokens_to_sample": 4096})) #TODO: check default max tokens and add explicitly if needed
            result = json.loads(response.get('body').read())
            responses.append((result.get('completion')))   #TODO: check if probability of completion can be returned
        return responses


class GPT(LLMBase):
    def __init__(self, model_name: str, cache_dir: str = "./llm_cache"):
        super().__init__(model_name, cache_dir)
        #self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(os.getenv('OPENAI_API_KEY'))

    def _generate_responses(self, prompt: str, num_samples: int, temperature = 0.7) -> List[Tuple[str, float]]:
        responses = []

        responses = self.client.chat.completions.create(
            model=self.model_name,
            messages = [
                {"role": "assistant", "content": ""},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4096,
            n=num_samples,
            temperature=temperature,
            #logprobs=True
        )
        assert len(responses["choices"]) == num_samples
        responses.extend(choice["message"]["content"] for choice in responses["choices"])
        
        return responses


class DeepSeekR1(LLMBase):
    def __init__(self, model_name: str, cache_dir: str = "./llm_cache"):
        super().__init__(model_name, cache_dir)
     
    def _generate_responses(self, prompt: str, num_samples: int, temperature = 0.7) -> List[Tuple[str, float]]:
        
        return [ollama.chat(model="deepseek-r1", options={"num_predict": 20}, messages=[{"role": "user", "content": prompt}])["message"]["content"] 
               for i in range(num_samples)]


#  client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))  

#     messages = [
#         {"role": "assistant", "content": ""},
#         {"role": "user", "content": prompt}
#     ]
#     response = client.chat.completions.create(
#         model=model_name,
#         messages=messages,
#         temperature=temperature,
#         max_tokens=max_tokens,
#     )
#     #print(response)
#     response_text = response.choices[0].message.content
#     return response_text


# def call_llama(prompt, model_name="meta-llama/Llama-3.1-8B-Instruct", temperature=0.7, max_tokens=256):
#     """
#     Prompts a Llama model using the Transformers library.

#     Args:
#         prompt (str): The input prompt for the model.
#         model_name (str): The Hugging Face model identifier.
#         temperature (float): Sampling temperature for randomness.
#         max_tokens (int): Maximum number of tokens to generate.

#     Returns:
#         str: The generated response.
#     """
#     # Load model and tokenizer
#     #print(model_name)
#     tokenizer = AutoTokenizer.from_pretrained(model_name)
#     model = AutoModelForCausalLM.from_pretrained(model_name)

#     # Encode the input prompt
#     inputs = tokenizer(prompt, return_tensors="pt")

#     # Generate output with specified parameters
#     outputs = model.generate(
#         inputs.input_ids,
#         max_new_tokens=max_tokens,
#         temperature=temperature,
#         do_sample=True,
#         top_k=50,  # Optional: Top-k sampling for diversity
#     )

#     # Decode and return the response
#     return tokenizer.decode(outputs[0], skip_special_tokens=True)


# def call_bedrock(prompt, model_name, temperature, max_tokens=256):
#     # Initialize Bedrock client
#     client = boto3.client(
#         service_name='bedrock-runtime',
#         aws_access_key_id=aws_access_key_id,
#         aws_secret_access_key=aws_secret_access_key,
#         region_name='us-east-1'
#     )

    
#     payload = {
#         "prompt": prompt,
#         "max_tokens_to_sample": max_tokens,
#         "temperature": temperature
#     }


#     # Call Bedrock API
#     response = client.invoke_model(
#         modelId=model_name,  
#         contentType='application/json',
#         accept='application/json',
#         body=json.dumps(payload)
#     )

#     # Parse and return result
#     result = json.loads(response.get('body').read())
#     return result.get('completion')


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
    #cache = Cache('./cache')

    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str, help="Path to the JSON file containing the prompt, model and parameter specifications.")
    args = parser.parse_args()
    

    # Load the configuration from the JSON file
    with open(args.config_file, 'r') as f:
        params = json.load(f)

    model_name = params["model_name"]
    prompt = params["prompt"]

    model_classes = {
        "anthropic": Claude,
        "meta-llama": Llama,
        "deepseek": DeepSeekR1,
        "gpt": GPT
    }
    
    # model = None

    # for prefix, model_class in model_classes.items():
    #     if model_name.startswith(prefix):
    #         model = model_class(model_name)
    #         break
      
    # if model == None:
    #     raise ValueError(f"Unsupported model: {model_name}")

    model = next((model_class(model_name) for prefix, model_class in model_classes.items() if model_name.startswith(prefix)), None)
    if model is None:
        raise ValueError(f"Unsupported model: {model_name}")
    
    response = model.get_response(params["prompt"], params["temperature"])
    print(response)
    # if 'prompt' not in params:
    #     raise ValueError("The JSON configuration file must include a 'prompt' field.")

    # Gets the response from the cache or by prompting the LLM
    # response = query_llm(**params)

    # # Print the response
    # print("LLM Response: ", response)
    
    #cache.close()
   
