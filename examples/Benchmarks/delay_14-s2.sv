module DELAY (input clk, input rst, output reg sig ,output reg err, output reg flg);
  localparam N = 100000;
  localparam CBITS = 17;
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
  s2: assert property (@(posedge clk) ((always s_eventually rst == 1) or (s_eventually always (flg == 1 s_until sig == 1)))) ;
  // F G (Verilog.DELAY.rst = FALSE) -> F G ((Verilog.DELAY.flg = TRUE) U (Verilog.DELAY.sig = TRUE))
endmodule
