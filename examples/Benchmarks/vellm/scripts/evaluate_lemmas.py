import json
import os
import sys
import argparse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import ROOT_DIR
from evaluation import LemmaEvaluator, VerificationResult

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--ebmc", action="store_true", help="Use EBMC model checker")
    parser.add_argument("--jg", action="store_true", help="Use JasperGold")
    parser.add_argument("--from_cache", action="store_true", help="Take verification result from cache, if cached")
    parser.add_argument("--only_cache", action="store_true", help="Get verification result only if cached. Returns a designated value if uncached")
    parser.add_argument("--cache_result", action="store_true", help="Caches verification result")

    args = parser.parse_args()

    input_json_path = os.path.join(ROOT_DIR, "scripts/results/proposed_lemmas.json")
    output_json_path = os.path.join(ROOT_DIR, "scripts/results/proposed_lemmas_eval.json")
    
    tool = "ebmc" if args.ebmc else "jg"  

    with open(input_json_path, "r") as f:
        lemmas_dict = json.load(f)
    
    evaluation_dict = lemmas_dict.copy()
 
    for module, models in lemmas_dict.items():

        sv_file = os.path.join(ROOT_DIR, f"hard_properties/{module}.sv")
        tcl_file = os.path.join(ROOT_DIR, f"hard_properties/tcl_files/{module}.tcl")
        lemma_evaluator = LemmaEvaluator(tool, sv_file, tcl_file, from_cache=args.from_cache, only_cache=args.only_cache, cache_result=args.cache_result)
        
        for model, data in models.items():
            for representation, lemmas in data.items():
                updated_lemmas = []
                for lemma in lemmas["lemmas"]:
                    #print(lemma)
                    updated_lemmas.append({"lemma": lemma,
                                           "correct": lemma_evaluator.is_correct(lemma).value,
                                           "useful": lemma_evaluator.is_useful(lemma).value})
                evaluation_dict[module][model][representation] = updated_lemmas
    
   
    with open(output_json_path, "w") as f:
        json.dump(evaluation_dict, f, indent=4)

 