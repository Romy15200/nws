#!/bin/bash

echo "Running get_lemmas.py..."
python3 get_lemmas.py --force_cached

echo "Running evaluate_lemmas.py..."
python3 evaluate_lemmas.py --jg --from_cache --only_cache 


