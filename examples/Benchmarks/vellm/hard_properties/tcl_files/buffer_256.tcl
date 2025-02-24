analyze -sv09 ../buffer_256.sv
elaborate
set_engine_mode M
reset -none -non_resettable_regs 0
clock clock
prove -all
