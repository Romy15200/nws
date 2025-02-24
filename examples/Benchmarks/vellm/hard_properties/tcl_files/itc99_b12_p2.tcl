
analyze -sv09 ../itc99_b12_p2.sv
elaborate
reset -none -non_resettable_regs 0
clock clock
prove -all
