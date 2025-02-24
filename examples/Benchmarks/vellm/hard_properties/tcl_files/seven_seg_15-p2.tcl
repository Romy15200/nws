
analyze -sv09 ../seven_seg_15-p2.sv
elaborate
reset rst
clock clk
prove -all
