analyze -sv09 /users/rompel/nws/examples/Benchmarks/vellm/hard_properties/gray_11-p3.sv
elaborate
reset -none
clock clk
prove -all
get_property_list -include {status {proven}}
