import json
import subprocess
import re
import shutil
import os
from utils import ROOT_DIR
from enum import Enum
from diskcache import Cache
import hashlib

ebmc_executable = "/home/ubuntu/hw-cbmc/src/ebmc/ebmc" # Path to the EBMC executable

JG_CORRECT_TIMEOUT = 3600
JG_HELPFUL_TIMEOUT = 600
BMC_BOUND = 50


class VerificationResult(Enum):
    PROVEN = 1
    CEX = 2
    TIMEOUT = 3
    ERROR = 4
    UNCACHED = 5

class VerilogModule:
    """Handles Verilog file modifications such as stripping assertions and adding assumptions."""

    def __init__(self, filepath, tcl_filepath=None):   #TODO: add support for reset & config info
        self.filepath = filepath
        self.module_name = os.path.splitext(os.path.basename(filepath))[0]
        with open(filepath, "r") as f:
                self.lines = f.readlines()
                
        #self.stripped_lines = self.module.strip_assertion()
        self.top = self._get_top()
        self.tcl = {"tcl_filepath": tcl_filepath, "tcl_lines": None}
        if tcl_filepath:
            with open(tcl_filepath, "r") as f:
                self.tcl["tcl_lines"] = f.readlines()

        self._assertion_index = self._find_assertion_index()
        assert self._assertion_index > 0 and self._assertion_index < len(self.lines)

    def get_config(self):
        return {"top": self.top}
    
    def _get_top(self):
        for line in self.lines:
            words = line.split()
            if "module" in words:  
                top = words[words.index("module") + 1]  # Extract next word
                return top

    def _find_assertion_index(self):
        pattern = re.compile(r"^\s*assert property")  # Match start of line, optional whitespace, then 'assert property'
        #TODO: see whether to support property label
        #print(self.filepath)
        #print(self.lines)
        matched_indices = [i for i, line in enumerate(self.lines) if pattern.match(line)]

        if len(matched_indices) == 0:
            raise ValueError("No 'assert property' found.")
        elif len(matched_indices) == 1:
            
            return matched_indices[0]  # Return the index of the matching line
        else:
            raise ValueError(f"Multiple 'assert property' lines found at indices: {matched_indices}")
        
     
    # def _strip_assertions(self):
    #     return self.lines[:self.assertion_index] + self.lines[self.assertion_index+1:]
    

    # def strip_property(self, lemma):
    #     """Returns the body of the lemma, without assert/assume"""    
    #     pattern = r"^\s*(?:assume|assert) property\s*\((.*)\)\s*;"
    #     match = re.search(pattern, lemma)
    #     return match.group(1) if match else None

    def _replace_action(self, text, action):
        """
        Finds an occurrence of 'assume' or 'assert' in a string and replaces it with the given mode.
        Ensures there is exactly one occurrence of either 'assume' or 'assert' in the string.

        Args:
            text (str): The input string containing 'assume' or 'assert'.
            action (str): The replacement string ('assume' or 'assert').

        Returns:
            str: The modified string with the replacement applied.

        Raises:
            ValueError: If there is not exactly one occurrence of 'assume' or 'assert'.
        """
        #print(text)
        if action not in {"assume", "assert"}:
            raise ValueError("action must be 'assume' or 'assert'")

        # Find all occurrences of "assume" or "assert"
        matches = re.findall(r"\b(?:assume|assert)\b", text)

        # Assert that there is exactly one occurrence
        assert len(matches) == 1, f"Expected exactly one occurrence of 'assume' or 'assert', found {len(matches)}."

        # Perform the replacement
        return re.sub(r"\b(?:assume|assert)\b", action, text, count=1) + ' \n'


    def add_property(self, lemma, new_file_path, new_tcl_path, action):
        """ Writes to new_file_path the verilog module, with the given line inserted where the original assertion was.
        Line is either an assertion or an assumption """
        #property = self._strip_property(lemma)
        #new_lines = f"{action} property {property} \n"
        new_lines = self._replace_action(lemma, action)
        modified_lines = self.lines[:]

        if action == "assert":
            modified_lines[self._assertion_index] = "// " + modified_lines[self._assertion_index]  #comment out  originial assertion

        modified_lines.insert(self._assertion_index, new_lines)
        #print(modified_lines)
        with open(new_file_path, "w", encoding="utf-8") as f:
            f.writelines(modified_lines)
       
        if new_tcl_path:
            self._write_new_tcl(new_file_path, new_tcl_path)
    

    def _write_new_tcl(self, new_file_path, new_tcl_path):
    
        modified_lines = [f"analyze -sv09 {new_file_path}\n" if "analyze -sv09" in line else line for line in self.tcl["tcl_lines"]]
        
        with open(new_tcl_path, "w") as f:
            f.writelines(modified_lines)



class LemmaEvaluator:
    """Evaluates a lemma using JG/EBMC."""

    def __init__(self, tool, verilog_file, tcl_file=None, ebmc_path=ebmc_executable, from_cache = False, only_cache = False, cache_result=False,
                 from_cache_skip_timeouts=False):
        if tool not in ["jg", "ebmc"]:
            raise ValueError("Please specify a model checker to use") 
        self.module = VerilogModule(verilog_file, tcl_file)
        self.ebmc_path = ebmc_path
        self.tool = tool
        self.cache = Cache(os.path.join(ROOT_DIR, 'eval_cache'))
        self.from_cache = from_cache
        self.only_cache = only_cache
        self.cache_result = cache_result
        self.from_cache_skip_timeouts = from_cache_skip_timeouts

    def _hash_query(self, lemma: str, mode: str) -> str:
        """Generate a hash for the lemma, mode and module name to use as a cache key."""
        #return hashlib.sha256(prompt.encode()).hexdigest()
        return hashlib.sha256(f"{lemma}-{mode}-{self.module.module_name}-{self.tool}".encode()).hexdigest()

    def _cache_result(self, lemma: str, mode: str, res: VerificationResult):
        #print(res)
        #print(res.value)
        #print(type(res))
        #print(type(res.value))
        cache_key = self._hash_query(lemma, mode)
        self.cache[cache_key] = res.value
        #self.cache.add(cache_key, res.value)
        #print(self.cache[cache_key])
        #print(type(self.cache[cache_key]))

    def _get_from_cache(self, lemma: str, mode: str):
        cache_key = self._hash_query(lemma, mode)
        if cache_key not in self.cache:
            return None
        
        return VerificationResult(self.cache[cache_key])    

    def process_lemma(self, lemma, mode):   
        """
        Creates a suitable sv and tcl files for the lemma with the given mode and runs JasperGold on them.
        Args:
            lemma (str): The lemma to add to the sv file.
            mode (str): Either "assert" or "assume".
        """
        if (self.from_cache or self.only_cache or self.from_cache_skip_timeouts):
            res = self._get_from_cache(lemma, mode)
            if res is not None and (not self.from_cache_skip_timeouts or res != VerificationResult.TIMEOUT):
                return res

        if self.only_cache and not self.from_cache_skip_timeouts:
            return VerificationResult.UNCACHED
            
        base_name = os.path.splitext(self.module.filepath)[0]
        new_tcl_path = f"{base_name}.lemma_temp.tcl"
        new_file_path = f"{base_name}.lemma_temp.sv"

        timeout = JG_CORRECT_TIMEOUT if mode == "assert" else JG_HELPFUL_TIMEOUT
        self.module.add_property(lemma, new_file_path, new_tcl_path, mode)

        if self.tool == "jg":
            res = self.run_jg(new_tcl_path, timeout=timeout)
        elif self.tool == "ebmc":
            res = self.run_ebmc(new_file_path, timeout=timeout)

        if self.cache_result:
            self._cache_result(lemma, mode, res)
        
        return res

    def is_correct(self, lemma):
        return self.process_lemma(lemma, "assert")

    
    def is_useful(self, lemma):
        return self.process_lemma(lemma, "assume")
        
    def run_jg(self, tcl_file_path, timeout):

        subprocess.run("rm -rf jgproject", shell=True)       
        command = f"jg -batch {tcl_file_path}"
        #print(tcl_file_path)
        try:
            res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=timeout, shell=True)
        except subprocess.TimeoutExpired as e:
            print(f"JasperGold timed out after {e.timeout} seconds")
            return VerificationResult.TIMEOUT 
        except Exception as e:
            print(f"[INFO] Error running JasperGold: {e}")
            return VerificationResult.ERROR 
        
        #print(res.stdout.splitlines())
        #print(type(res.stdout.splitlines()))
        #TODO: Find a better way to extract result and handle errors
        if any("ERROR" in line for line in res.stdout.splitlines()):
            return VerificationResult.ERROR
        #print(res.stdout.splitlines())
        
        proven = any("- proven" in line and "1 (100%)" in line for line in res.stdout.splitlines()) 
        assert not proven or  (not any("get_property_list -include {status {proven}}" in line for line in res.stdout.splitlines())) or \
                              (not any("No properties matched the specified filters." in line for line in res.stdout.splitlines()))
        
        assert proven or (not any("get_property_list -include" in line for line in res.stdout.splitlines())) or ((not any("get_property_list -include {status {cex}}") in line for line in res.stdout.splitlines()) or 
                          (not any("No properties matched the specified filters." in line for line in res.stdout.splitlines())))
        
        res = VerificationResult.PROVEN if proven else VerificationResult.CEX
        return res
    

    def run_ebmc(self, sv_file_path, timeout, bmc_bound = BMC_BOUND):
        """Runs EBMC on the given Verilog file and returns True if it passes verification.""" 
        config = self.module.get_config()

        # command = list(filter(None, [   
        #     self.ebmc_path,
        #     sv_file_path,
        #     f"--bound {bmc_bound}",
        #     f"--top {config["top"]}"
        # #    module_config if module_config else None
        # ]))
        
        command = f"{self.ebmc_path} {sv_file_path} --bound {bmc_bound}, --top {config['top']}"
       
        try:    
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, shell=True)
            #print(result.stdout) 
            #print(result.stderr)
            #print(result.returncode)
        except subprocess.TimeoutExpired as e:
            print(f"EBMC timed out after {e.timeout} seconds")
            return VerificationResult.TIMEOUT 
        except Exception as e:
            print(f"Error running EBMC: {e}")
            return VerificationResult.ERROR
        
        if result.stderr != "":
            print(f"Error running EBMC on file {sv_file_path}: {result.stderr}")
            return VerificationResult.ERROR
        
        print(result.stdout)
        if f"PROVED up to bound {bmc_bound}" in result.stdout:
            return VerificationResult.PROVEN
        
       
        if f"REFUTED" in result.stdout:
            return VerificationResult.CEX
        
        


if __name__ == "__main__":
    lemma_eval = LemmaEvaluator("jg", '/users/rompel/nws/examples/Benchmarks/vellm/hard_properties/gray_11-p3.sv', '/users/rompel/nws/examples/Benchmarks/vellm/hard_properties/tcl_files/gray_11-p3.tcl')
    print(lemma_eval.run_jg('/users/rompel/nws/examples/Benchmarks/vellm/hard_properties/tcl_files/gray_11-p3.tcl', timeout=100).value)