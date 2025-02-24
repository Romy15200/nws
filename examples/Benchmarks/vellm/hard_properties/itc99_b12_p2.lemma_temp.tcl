
analyze -sv09 /home/ubuntu/nws/examples/Benchmarks/vellm/hard_properties/itc99_b12_p2.lemma_temp.sv
elaborate
reset -none -non_resettable_regs 0
clock clock
prove -all
