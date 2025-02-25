
analyze -sv09 ../seven_seg_15-p2.sv
elaborate
reset -none
clock clk
prove -all
