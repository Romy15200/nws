
analyze -sv09 /home/ubuntu/nws/examples/Benchmarks/vellm/hard_properties/am2910_parametrized_p4.lemma_temp.sv
elaborate -bbox_a 1000000000
reset -none -non_resettable_regs 0
clock clk
prove -all
