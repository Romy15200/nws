package my_package;
  checker myChecker(input logic [31:0] data);
    assert property (data != 10);
  endchecker
endpackage

module main(input clk);
  reg [31:0] counter = 0;
  always_ff @(posedge clk) counter++;
  my_package::myChecker c(counter);
endmodule
