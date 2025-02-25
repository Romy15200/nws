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
from utils import ROOT_DIR 
import time

CACHE = os.path.join(ROOT_DIR, "llm_cache")

class LLMBase(ABC):
    def __init__(self, model_name: str, cache_dir: str = CACHE):
        self.model_name = model_name
        self.cache = Cache(cache_dir)

    def _hash_query(self, prompt: str) -> str:
        """Generate a hash for the prompt and model name to use as a cache key."""
        #return hashlib.sha256(prompt.encode()).hexdigest()
        return hashlib.sha256(f"{prompt}-{self.model_name}".encode()).hexdigest()
    
    def _sample_from_responses(self, responses: List[Tuple[str, float]], temperature: float) -> Tuple[str, float]:
        """Sample a response uniformly at random"""
        random.seed(42)  
        if temperature == 0:
            return responses[0]  # deterministic: always return the first response
        return random.choices(responses, k=1)[0]

    def get_response(self, prompt: str, temperature: float = 0.7, clear = False, force_cached = False) -> Tuple[str, float]:
        """
        Check cache or generate new responses.
        Returns the response and whether it was in the cache.
        If clear == True, the corresponding entry in the cache is deleted and get_response returns 
        whether the entry existed in the cache, together with the newly generated response.
        """
        
        query_hash = self._hash_query(prompt)
        cache_hit = query_hash in self.cache

        if clear:
            self.cache.delete(query_hash)
        
        responses = self.cache[query_hash] if (cache_hit and not clear) \
            else self._generate_responses(prompt) if not force_cached else None
        if (not cache_hit or clear) and not force_cached:
            self.cache[query_hash] = responses  # store in cache

        
        response = self._sample_from_responses(responses, temperature) if responses else None

        return {"cache_hit": cache_hit, "response": response}

    def cache_more(self, prompt: str, num_samples: int = 1, temperature=0.7):
        """Generate multiple responses for a prompt and add to cache"""
        query_hash = self._hash_query(prompt)
        responses = self._generate_responses(prompt, num_samples=num_samples)
        if query_hash in self.cache:
            self.cache[query_hash].extend(responses)
        else:
            self.cache.add(query_hash, responses)
    
    def get_num_samples(self, prompt:str) -> int:
        query_hash = self._hash_query(prompt)
        if query_hash not in self.cache:
            return 0
        else:
            return len(self.cache[query_hash])



    @abstractmethod
    def _generate_responses(self, prompt: str, num_samples: int = 5, temperature=0.7) -> List[Tuple[str, float]]: 
        """Generate multiple responses along with their probabilities for a prompt."""
        pass


class Llama(LLMBase):
    def __init__(self, model_name: str, cache_dir: str = CACHE):
        super().__init__(model_name, cache_dir)
        self.model_name = model_name  

    def _generate_responses(self, prompt: str, num_samples: int, temperature = 0.7) -> List[Tuple[str, float]]:
        #if not hasattr(self, "device"):
        #    self.device =  0 if torch.cuda.is_available() else -1
        if not hasattr(self, "generator"):
            #self.generator = pipeline("text-generation", model=self.model_name, device=self.device)
            self.generator = pipeline("text-generation", model=self.model_name, device_map="auto")
            
        responses = []
        for _ in range(num_samples):
            response = self.generator(prompt, num_return_sequences=1, return_full_text=False, max_new_tokens=5000)
            responses.append(response[0]["generated_text"])  
        
        #responses = self.generator(prompt, num_return_sequences=num_samples, return_full_text=False, max_new_tokens = 6000)
        return responses


class Claude(LLMBase):
    def __init__(self, model_name: str, cache_dir: str = CACHE):
        super().__init__(model_name, cache_dir)
        
    #TODO: max retries for anthropic.claude-v2:1 is 4? Throws throttling exception. 
    def _generate_responses(self, prompt: str, num_samples: int = 2, temperature = 0.7) -> List[Tuple[str, float]]:
        if not hasattr(self, "client"):
            aws_config = {
                "aws_access_key_id": os.getenv('AWS_ACCESS_KEY_ID'),
                "aws_secret_access_key": os.getenv('AWS_SECRET_ACCESS_KEY'),
                "region_name": os.getenv('AWS_REGION_NAME'),
            }
            self.client = boto3.client("bedrock-runtime", **{k: v for k, v in aws_config.items() if v is not None})
        
        # self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        # self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')     
        # self.region_name = os.getenv('AWS_REGION_NAME')
        
        # self.client = boto3.client("bedrock-runtime", aws_access_key_id=self.aws_access_key_id, 
        #                            aws_secret_access_key=self.aws_secret_access_key, region_name=self.region_name)
        
        responses = []
        prompt = "\n\nHuman: " + prompt + "\n\nAssistant: "
        #print(prompt)
        
        for _ in range(num_samples):
            try:
                response = self.client.invoke_model(modelId=self.model_name, contentType='application/json', 
                                                    accept='application/json', body=json.dumps({"prompt": prompt, "max_tokens_to_sample": 4096})) #TODO: check default max tokens and add explicitly if needed
                result = json.loads(response.get('body').read())
            except Exception as e:
                print(f"[ERROR] Prompting {self.model_name}: {e}")
                continue

            responses.append((result.get('completion')))   #TODO: check if probability of completion can be returned
            time.sleep(2)

        return responses


class GPT(LLMBase):
    def __init__(self, model_name: str, cache_dir: str = "./llm_cache"):
        super().__init__(model_name, cache_dir)
        #self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.client = None

    def _generate_responses(self, prompt: str, num_samples: int = 5, temperature = 0.7) -> List[Tuple[str, float]]:
        
        if self.client is None:
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
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
        assert len(responses.choices) == num_samples
        #responses.extend(choice.message.content for choice in responses["choices"])
        
        return [choice.message.content for choice in responses.choices]


class DeepSeekR1(LLMBase):
    def __init__(self, model_name: str, cache_dir: str = "./llm_cache"):
        super().__init__(model_name, cache_dir)
     
    def _generate_responses(self, prompt: str, num_samples: int, temperature = 0.7) -> List[Tuple[str, float]]:
        
        return [ollama.chat(model="deepseek-r1", messages=[{"role": "user", "content": prompt}])["message"]["content"] 
               for i in range(num_samples)]

def prompt_llms(config_file, **kwargs):
    temperature = kwargs.pop("temperature", 0.7)
    clear = kwargs.pop("clear", False)
    force_cached = kwargs.pop("force_cached", False)
    
    # Load prompt and model name from the JSON file
    with open(config_file, 'r') as f:
        params = json.load(f)

    model_name = params["model_name"]
    prompt = params["prompt"]

    model_classes = {
        "anthropic": Claude,
        "meta-llama": Llama,
        "deepseek": DeepSeekR1,
        "gpt": GPT
    }
       
    model = next((model_class(model_name) for prefix, model_class in model_classes.items() if model_name.startswith(prefix)), None)
    if model is None:
        raise ValueError(f"Unsupported model: {model_name}")
    
    result = model.get_response(prompt, temperature, clear=clear, force_cached=force_cached)

    return result

def main():
    # Initialize cache
    #cache = Cache('./cache')

    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str, help="Path to the JSON file containing the prompt, model and parameter specifications.")
    parser.add_argument('--clear', action="store_true", help="Clear cache entry and force prompting underlying llm. Saves new response in cache")
    parser.add_argument('--force_cached', action="store_true", help="Return response only if cached")
    parser.add_argument('--temperature', help="Temperature according to which to sample, not supported yet")
    args = parser.parse_args()
    
    kwargs = {key: value for key, value in vars(args).items() if key in {"clear", "force_cached", "temperature"} and value is not None}

    result = prompt_llms(args.config_file, **kwargs)
   
    print(result["response"])
 



if __name__ == "__main__":
    main()
   
