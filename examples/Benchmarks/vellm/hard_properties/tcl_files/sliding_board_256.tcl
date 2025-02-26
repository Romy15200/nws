
analyze -sv09 ../sliding_board_256.sv
elaborate -bbox_a 10000000 -loop_limit 100000
reset -none -non_resettable_regs 0
clock clock
prove -all
