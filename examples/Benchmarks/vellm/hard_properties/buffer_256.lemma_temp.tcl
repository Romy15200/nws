analyze -sv09 /users/rompel/nws/examples/Benchmarks/vellm/hard_properties/buffer_256.lemma_temp.sv
elaborate
set_engine_mode M
reset -none -non_resettable_regs 0
clock clock
prove -all
