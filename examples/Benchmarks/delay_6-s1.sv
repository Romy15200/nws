module DELAY (input clk, input rst, output reg sig ,output reg err, output reg flg);
  localparam N = 10000;
  localparam CBITS = 14;
  reg [CBITS-1 :0] cnt;
  always @(posedge clk) begin
    if (rst) cnt = 0;
    else cnt = cnt + 1;
    if (cnt > N) begin sig = 1;
      cnt = 0; end
    else sig = 0;
    if (cnt > N + 1) err = 1;
    else err = 0;
    if (cnt <= N) flg = 1;
    else flg = 0;
  end
  s1: assert property (@(posedge clk) ((always s_eventually rst == 1) or (always s_eventually sig == 1)) and (nexttime always err == 0)) ;
  // (F G (Verilog.DELAY.rst = FALSE) -> G F (Verilog.DELAY.sig = TRUE)) & (X G Verilog.DELAY.err = FALSE)
endmodule
