import json
import os
import sys
import io
import argparse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import ROOT_DIR
from evaluation import LemmaEvaluator, VerificationResult
import pandas as pd


def display_in_table(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)


    results = {}

    for _, models in data.items():
        for model, representations in models.items():
            if model not in results:
                results[model] = {
                "Total Lemmas": 0,
                "Only Useful": 0,
                "Only Correct": 0,
                "Useful + Correct": 0,
            }

            # Iterate over all lemma representations
            for _, lemmas_list in representations.items():
                for lemma_entry in lemmas_list:
                    results[model]["Total Lemmas"] += 1
                    correct = lemma_entry["correct"]
                    useful = lemma_entry["useful"]

                    # 1 is "success", 2,3,4 are failure
                    is_correct = (correct == 1)
                    is_useful = (useful == 1)

                    if is_correct and is_useful:
                        results[model]["Useful + Correct"] += 1
                    elif is_correct:
                        results[model]["Only Correct"] += 1
                    elif is_useful:
                        results[model]["Only Useful"] += 1

            # Store results for the current model
            

    df = pd.DataFrame.from_dict(results, orient="index")
    print(df)


if __name__ == "__main__":
    #sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument("--ebmc", action="store_true", help="Use EBMC model checker")
    parser.add_argument("--jg", action="store_true", help="Use JasperGold")
    parser.add_argument("--from_cache", action="store_true", help="Take verification result from cache, if cached")
    parser.add_argument("--only_cache", action="store_true", help="Get verification result only if cached. Returns a designated value if uncached")
    parser.add_argument("--cache_result", action="store_true", help="Caches verification result")
    parser.add_argument("--from_cache_skip_timeouts", action="store_true", help="Returns verification result from cache if exists and not timeout")

    args = parser.parse_args()
    if args.jg and args.ebmc:
        print("Error: The arguments '--jg' and '--ebmc' are mutually exclusive. Please provide only one.")
        exit(1)  

    input_json_path = os.path.join(ROOT_DIR, "scripts/results/proposed_lemmas.json")
   
    
    tool = "ebmc" if args.ebmc else "jg"  
    output_json_path = os.path.join(ROOT_DIR, f"scripts/results/proposed_lemmas_eval_{tool}.json")

    with open(input_json_path, "r") as f:
        lemmas_dict = json.load(f)
    
    evaluation_dict = lemmas_dict.copy()
 
    for module, models in lemmas_dict.items():
        print(f"Processing module {module}")
        sv_file = os.path.join(ROOT_DIR, f"hard_properties/{module}.sv")
        tcl_file = os.path.join(ROOT_DIR, f"hard_properties/tcl_files/{module}.tcl")
        lemma_evaluator = LemmaEvaluator(tool, sv_file, tcl_file, from_cache=args.from_cache, only_cache=args.only_cache, cache_result=args.cache_result
                                         , from_cache_skip_timeouts=args.from_cache_skip_timeouts, ebmc_path='ebmc')
        
        for model, data in models.items():   
            for representation, lemmas in data.items():
                updated_lemmas = []
                for lemma in lemmas["lemmas"]:
                    #print(f"Processing lemma {lemma}")
                    updated_lemmas.append({"lemma": lemma,
                                           "correct": lemma_evaluator.is_correct(lemma).value,
                                           "useful": lemma_evaluator.is_useful(lemma).value})
                evaluation_dict[module][model][representation] = updated_lemmas
    
   
    with open(output_json_path, "w") as f:
        json.dump(evaluation_dict, f, indent=4)

    display_in_table(output_json_path)
 