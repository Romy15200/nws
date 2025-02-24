
analyze -sv09 ../am2910_parametrized_p4.sv
elaborate -bbox_a 1000000000
reset -none -non_resettable_regs 0
clock clk
prove -all
