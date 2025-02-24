import json
import subprocess
import re
import shutil
import os
from utils import ROOT_DIR

ebmc_executable = "/home/romy.peled/hw-cbmc/src/ebmc/ebmc" # Path to the EBMC executable

JG_CORRECT_TIMEOUT = 300
JG_HELPFUL_TIMEOUT = 300

class VerilogModule:
    """Handles Verilog file modifications such as stripping assertions and adding assumptions."""

    def __init__(self, filepath, tcl_filepath=None):   #TODO: add support for reset & config info
        self.filepath = filepath
        with open(filepath, "r") as f:
            self.lines = f.readlines()
       
        #self.stripped_lines = self.module.strip_assertion()
        
        self.tcl = {"tcl_filepath": tcl_filepath, "tcl_lines": None}
        if tcl_filepath:
            with open(tcl_filepath, "r") as f:
                self.tcl["tcl_lines"] = f.readlines()

        self._assertion_index = self._find_assertion_index()
        assert self._assertion_index > 0 and self._assertion_index < len(self.lines)


    def _find_assertion_index(self):
        pattern = re.compile(r"^\s*assert property")  # Match start of line, optional whitespace, then 'assert property'
        #TODO: see whether to support property label
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

    # """
    # def add_assumption(self, lemma, new_file_path, new_tcl_path = None):
    #     """Writes to new_file_path the verilog module with the lemma inserted as an assumption.
    #     If new_tcl_path is supplied, a suitable tcl is written to it"""
    #     assumption = f"assume ({self.strip_property(lemma)});\n"
    #     self._add_property(assumption, new_file_path, new_tcl_path)
        
        
        
        
    #     endmodule_index = next(
    #         i for i in range(len(self.lines) - 1, -1, -1) if self.lines[i].strip() == "endmodule"
    #     )
    #     new_lines = self.lines[:endmodule_index] + [assumption] + self.lines[endmodule_index:]
    
    #     with open(new_file_path, "w") as f:
    #         f.writelines(new_lines)
    #     # # Find "endmodule" and insert the lemma before it
    #     # for i in range(len(lines) - 1, -1, -1):
    #     #     if re.match(r"^\s*endmodule\s*$", lines[i]):
    #     #         lines.insert(i, f"{lemma}\n")
    #     #         break
    #     # self.lines.append(assumption)  # Append the assumption at the end
        
        
    # def add_assertion(self, lemma, new_file_path):
    #     """Writes to new_file_path the verilog module with the given lemma as an assertion"""
    #     assertion = f"assert ({self.strip_property(lemma)});\n"
    #     self._add_property(assertion, new_file_path)
    # """

    def get_config():
        return None



class LemmaEvaluator:
    """Evaluates a lemma using JG/EBMC."""

    def __init__(self, verilog_file, tcl_file=None):
        self.module = VerilogModule(verilog_file, tcl_file)
        #self.ebmc_path = ebmc_path
        

    def is_correct_ebmc(self, lemmas):
        # temp_file = "temp_no_assert.sv"
        # return {lemma: self.run_ebmc(self.module.add_assertion(lemma, temp_file), self.module.get_config()) for lemma in lemmas}
        pass

    def process_lemma(self, lemma, mode):   
        """
        Creates a suitable sv and tcl files for the lemma with the given mode and runs JasperGold on them.
        Args:
            lemma (str): The lemma to add to the sv file.
            mode (str): Either "assert" or "assume".
        """
        base_name = os.path.splitext(self.module.filepath)[0]
        new_tcl_path = f"{base_name}.lemma_temp.tcl"
        new_file_path = f"{base_name}.lemma_temp.sv"

        timeout = JG_CORRECT_TIMEOUT if mode == "assert" else JG_HELPFUL_TIMEOUT
        self.module.add_property(lemma, new_file_path, new_tcl_path, mode)

        return self.run_jg(new_tcl_path, timeout=timeout)



    def is_correct_jg(self, lemma):
        # base_name = os.path.splitext(self.module.filepath)[0]
        # new_tcl_path = f"{base_name}.lemma_temp.tcl"
        # new_file_path = f"{base_name}.lemma_temp.sv"
        
        # self.module.add_property(lemma, new_file_path, new_tcl_path, "assert") 
        # #print(new_tcl_path)
        # #print(new_file_path)
        # self.run_jg(new_tcl_path)
        return self.process_lemma(lemma, "assert")

    
    def is_useful_jg(self, lemma):
        return self.process_lemma(lemma, "assume")
        
    def run_jg(self, tcl_file_path, timeout):
        subprocess.run("rm -rf jgproject", shell=True)
        command = f"jg -batch {tcl_file_path}"
        #print(tcl_file_path)
        try:
            res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=timeout, shell=True)
        except subprocess.TimeoutExpired as e:
            print(f"Command timed out after {e.timeout} seconds")
            return 
        except Exception as e:
            print(f"Error running JasperGold: {e}")
            return 

       
        proven = any("- proven" in line and "1 (100%)" in line for line in res.stdout.splitlines()) #TODO: find a better way to extract result
        #print(res.stdout.splitlines())
        #print(res.stderr.splitlines())

        
        return proven
    

    def extract_property(self, lemma):
        pass

    

    def run_ebmc(self, sv_file_path, module_config=None):
        """Runs EBMC on the given Verilog file and returns True if it passes verification.""" 
        try:
            command = list(filter(None, [   
                self.ebmc_path,
                module_config if module_config else None
            ]))
           
            result = subprocess.run(command, capture_output=True, text=True)
            return "" in result.stdout
        
        except Exception as e:
            print(f"Error running EBMC: {e}")
            return False
        



