import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import ROOT_DIR
from evaluation import LemmaEvaluator

def main():
    input_json_path = os.path.join(ROOT_DIR, "scripts/results/proposed_lemmas.json")
    output_json_path = os.path.join(ROOT_DIR, "results/proposed_lemmas_eval.json")
    
    with open(input_json_path, "r") as f:
        lemmas_dict = json.load(f)

    evaluation_dict = lemmas_dict.copy()
    for module, models in lemmas_dict.items():
        print(module)
        sv_file = os.path.join(ROOT_DIR, f"hard_properties/{module}.sv")
        tcl_file = os.path.join(ROOT_DIR, f"hard_properties/tcl_files/{module}.tcl")
        lemma_evaluator = LemmaEvaluator(sv_file, tcl_file)
        
        for model, data in models.items():
            for representation, lemmas in data.items():
                updated_lemmas = []
                for lemma in lemmas["lemmas"]:
                    #print(lemma)
                    updated_lemmas.append({"lemma": lemma,
                                           "correct": lemma_evaluator.is_correct_jg(lemma),
                                           "useful": lemma_evaluator.is_useful_jg(lemma)})
                evaluation_dict[module][model][representation] = updated_lemmas
    
    with open("output_json_path", "w") as f:
        json.dump(evaluation_dict, f)

 

if __name__ == "__main__":
    main()
