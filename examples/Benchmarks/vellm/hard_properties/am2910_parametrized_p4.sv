/*
*
*	Taken from VIS Benchmarks <ftp://vlsi.colorado.edu/pub/vis/vis-verilog-models-1.3.tar.gz>
*	Modified by Ahmed Irfan <irfan@fbk.eu>
*
*/
module am2910(I,CCEN_BAR,CC_BAR,RLD_BAR,CI,OEbar,clk,D,Y,PL_BAR,
	      VECT_BAR,MAP_BAR,FULL_BAR);
    localparam MBITS = 2048;
    localparam S_SIZE = 4096;
    localparam LOG_S_SIZE = 12;

    input [3:0]	  I;
    input	  CCEN_BAR;
    input	  CC_BAR;
    input	  RLD_BAR;
    input	  CI;
    input	  OEbar;
    input	  clk;
    input [MBITS-1:0]  D;
    output [MBITS-1:0] Y;
    output	  PL_BAR;
    output	  VECT_BAR;
    output	  MAP_BAR;
    output	  FULL_BAR;

    reg [LOG_S_SIZE-1:0] sp;			// stack pointer
    wire	  R_sel;
    wire	  D_sel;
    wire	  uPC_sel;
    wire	  stack_sel;
    wire	  decr;
    wire	  load;
    wire	  Rzero_bar;
    wire	  clear;
    wire	  push;
    wire	  pop;

    wire [MBITS-1:0]   CI_ext;		// vl2mv fix
    wire [MBITS-1:0]	  Y_temp;
    reg [MBITS-1:0]	  RE;			// iteration counter
    reg [MBITS-1:0]	  uPC;			// micro-program counter
    reg [MBITS-1:0]	  reg_file[S_SIZE-1:0];	// micro-program stack
    wire [LOG_S_SIZE-1:0]	  write_address;
    wire	  fail;

    integer	  i;

   reg            old;
   reg [LOG_S_SIZE-1:0] sp_old;
   reg [MBITS-1:0] reg_file0_old;
   reg [MBITS-1:0] reg_file5_old;
   
    initial reg_file[0] = 12'b0;
    initial begin
	RE = {MBITS{1'b0}};  //RE = 12'd0;
	uPC = {MBITS{1'b0}}; //uPC = 12'd0;
	sp = 8'd4;//{LOG_S_SIZE{1'b0}}; //sp = 3'd0;
        reg_file0_old = {MBITS{1'b0}};
        reg_file[0] = 12'd0;
        reg_file[1] = {MBITS{1'b0}};
        reg_file[2] = {MBITS{1'b0}};
        reg_file[3] = 12'd0;
        reg_file[4] = {MBITS{1'b0}};
        old = 1'b0;
       //for (i = 0; i < S_SIZE; i = i + 1) 
       //begin
//	 reg_file[i] = {MBITS{1'b0}};  //reg_file[i] = 12'd0
//       end
    end 

    assign CI_ext[MBITS-1:1] = {(MBITS-1){1'b0}}; //assign CI_ext[11:1] = 11'd0;
    assign CI_ext[0] = CI;
    assign Y_temp = R_sel ? RE : D_sel ? D : uPC_sel ? uPC :
	stack_sel ? reg_file[sp] : {MBITS{1'b0}};

    // Ignoring tri-state buffers.
    assign Y = Y_temp;

    always @ (posedge clk) begin
	if (load | ~RLD_BAR)
	    RE <= D;
	else if (decr & RLD_BAR)
	    RE <= RE - {{(MBITS-1){1'b0}}, {1'b1}};

	if (clear)
	    uPC <= {MBITS{1'b0}};
	else
	    uPC <= Y_temp + CI_ext;
	
	if (pop && sp != {LOG_S_SIZE{1'b0}})
	    sp <= sp - {{(LOG_S_SIZE-1){1'b0}}, {1'b1}};
	else if (push & sp != S_SIZE-1)
            sp <= sp + {{(LOG_S_SIZE-1){1'b0}}, {1'b1}};//sp <= sp + 3'd1;
	else if (clear)
	    sp <= {LOG_S_SIZE{1'b0}};//sp <= 3'd0;

	if (push)
	    reg_file[write_address] <= uPC;

       old <= 1'b1;
       
	sp_old <= sp;
	reg_file0_old <= reg_file[0];
	reg_file5_old <= reg_file[5];
    end // always @ (posedge clk)

    assign Rzero_bar = |RE[(MBITS-1):0];
    assign write_address = (sp != S_SIZE-1) ? sp + {{(LOG_S_SIZE-1){1'b0}}, {1'b1}} : sp;
    assign FULL_BAR = sp == S_SIZE-1;

    assign fail = CC_BAR & ~ CCEN_BAR;
    assign D_sel = 
	(I == 4'd2) |
	(Rzero_bar & (I == 4'd9)) |
	(~Rzero_bar & fail & (I == 4'd15)) |
	(~fail & ((I == 4'd1) | (I == 4'd3) | (I == 4'd5) | (I == 4'd7) |
		  (I == 4'd11)));
    assign uPC_sel =
	(I == 4'd4) | (I == 4'd12) | (I == 4'd14) |
	(fail & ((I == 4'd1) | (I == 4'd3) | (I == 4'd6) | (I == 4'd10) |
		 (I == 4'd11) | (I == 4'd14))) |
	(~Rzero_bar & ((I == 4'd8) | (I == 4'd9))) |
	(~fail & ((I == 4'd15) | (I == 4'd13)));
    assign stack_sel =
	(Rzero_bar & (I == 4'd8)) |
	(~fail & (I == 4'd10)) |
	(fail & (I == 4'd13)) |
	(Rzero_bar & fail & (I == 4'd15));
    assign R_sel = fail & ((I == 4'd5) | (I == 4'd7));
    assign push = (~fail & (I == 4'd1)) | (I == 4'd4) | (I == 4'd5);
    assign pop =
	(~fail & ((I == 4'd10) | (I == 4'd11) | (I == 4'd13) | (I == 4'd15))) |
	(~Rzero_bar & ((I == 4'd8) | (I == 4'd15)));
    assign load = (I == 4'd12) | (~fail & (I == 4'd4));
    assign decr = Rzero_bar & ((I == 4'd8) | (I == 4'd9) | (I == 4'd15));
    assign MAP_BAR = I == 4'd2;
    assign VECT_BAR = I == 4'd6;
    assign PL_BAR = (I == 4'd2) | (I == 4'd6);
    assign clear = I == 4'd0;

	//#PASS: The antecedent is never satisfied for the reachable states.
	//assert property G(reg_file<*0*>[11:0]=0 * !sp[2:1]=b11);
        //assert property (reg_file[0]==0 && sp <= S_SIZE-1);
	//assert property (@(posedge clk) reg_file[0]==0);
        //#PASS: the 0-th entry of the stack is never written and the stack pointer
	//# is never 6 or 7.
	//assert property G(sp[2:0]=6 -> X(sp[2:0]=7));
	
	//#PASS: The antecedent is never satisfied for the reachable states.
	// assert property G(reg_file<*0*>[11:0]=b000000000010 -> X(reg_file<*0*>[11:0]=b000000000001));
	
	//#PASS: the contents of the fifth entry of the stack cannot change in the
	//# next clock cycle unless the stack pointer is either 4 or 5.
	// assert property G(!(sp[2:0]=b100) * !(sp[2:0]=b101) -> (reg_file<*5*>[11:0]=b101010101010 -> X(reg_file<*5*>[11:0]=b101010101010)));
	
        initial begin
	   sp_old = {LOG_S_SIZE{1'b0}};  //sp_old = 3'd0;
	   reg_file0_old = {MBITS{1'b0}};
	   reg_file5_old = {MBITS{1'b0}};
	end
      // assert property (@(posedge clk)(old == 1'b0 || !(sp_old!= 3'd4 && sp_old != 3'd5) || reg_file5_old == reg_file[5]));
//assert property (@(posedge clk) (old == 1'b0 || !(sp_old!= 4 && sp_old != 5) || $stable(reg_file[5])));
assert property (@(posedge clk) ((sp != 0 and sp!= (S_SIZE-2) and sp != (S_SIZE -1) and sp!= S_SIZE and $past(push) == 1 and pop == 1) |=> (reg_file[sp] == $past(reg_file[sp],2))));
endmodule // am2910
