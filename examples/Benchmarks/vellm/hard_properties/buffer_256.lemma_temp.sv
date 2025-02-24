/*
*
*	Taken from VIS Benchmarks <ftp://vlsi.colorado.edu/pub/vis/vis-verilog-models-1.3.tar.gz>
*	Modified for YOSYS BTOR Backend <http://www.clifford.at/yosys/>
*	Modified by Ahmed Irfan <irfan@fbk.eu>
*
*/
// Buffer allocation model derived from Ken McMillan's.
// The modifications were meant to adapt the description to the requirements
// of vl2mv.
//
// Author: Fabio Somenzi <Fabio@Colorado.EDU>
//
module main (
    clock,
    alloc_raw,
    // nack,
    // alloc_addr,
    free_raw,
    free_addr_raw
);
`define SIZE 128
`define LOGSIZE 7
  input clock;
  input alloc_raw;
  input free_raw;
  input [(`LOGSIZE-1):0] free_addr_raw;

  reg       busy  [0:(`SIZE - 1)];
  reg [`LOGSIZE:0] count;
  reg alloc, free;
  reg     [(`LOGSIZE-1):0] free_addr;
  integer           i;
  wire              nack;
  wire    [(`LOGSIZE-1):0] alloc_addr;

  initial begin
    for (i = 0; i < `SIZE; i = i + 1) busy[i] = 0;
    count = 0;
    alloc = 0;
    free = 0;
    free_addr = 0;
  end

  assign nack = alloc & (count == `SIZE);
  
    assign alloc_addr =
               ~busy[0] ? 0 :
               ~busy[1] ? 1 :
               ~busy[2] ? 2 :
               ~busy[3] ? 3 :
               ~busy[4] ? 4 :
               ~busy[5] ? 5 :
               ~busy[6] ? 6 :
               ~busy[7] ? 7 :
               ~busy[8] ? 8 :
               ~busy[9] ? 9 :
               ~busy[10] ? 10 :
               ~busy[11] ? 11 :
               ~busy[12] ? 12 :
               ~busy[13] ? 13 :
               ~busy[14] ? 14 :
               ~busy[15] ? 15 :
               ~busy[16] ? 16 :
               ~busy[17] ? 17 :
               ~busy[18] ? 18 :
               ~busy[19] ? 19 :
               ~busy[20] ? 20 :
               ~busy[21] ? 21 :
               ~busy[22] ? 22 :
               ~busy[23] ? 23 :
               ~busy[24] ? 24 :
               ~busy[25] ? 25 :
               ~busy[26] ? 26 :
               ~busy[27] ? 27 :
               ~busy[28] ? 28 :
               ~busy[29] ? 29 :
               ~busy[30] ? 30 :
               ~busy[31] ? 31 :
               ~busy[32] ? 32 :
               ~busy[33] ? 33 :
               ~busy[34] ? 34 :
               ~busy[35] ? 35 :
               ~busy[36] ? 36 :
               ~busy[37] ? 37 :
               ~busy[38] ? 38 :
               ~busy[39] ? 39 :
               ~busy[40] ? 40 :
               ~busy[41] ? 41 :
               ~busy[42] ? 42 :
               ~busy[43] ? 43 :
               ~busy[44] ? 44 :
               ~busy[45] ? 45 :
               ~busy[46] ? 46 :
               ~busy[47] ? 47 :
               ~busy[48] ? 48 :
               ~busy[49] ? 49 :
               ~busy[50] ? 50 :
               ~busy[51] ? 51 :
               ~busy[52] ? 52 :
               ~busy[53] ? 53 :
               ~busy[54] ? 54 :
               ~busy[55] ? 55 :
               ~busy[56] ? 56 :
               ~busy[57] ? 57 :
               ~busy[58] ? 58 :
               ~busy[59] ? 59 :
               ~busy[60] ? 60 :
               ~busy[61] ? 61 :
               ~busy[62] ? 62 :
               ~busy[63] ? 63 :
               ~busy[64] ? 64 :
               ~busy[65] ? 65 :
               ~busy[66] ? 66 :
               ~busy[67] ? 67 :
               ~busy[68] ? 68 :
               ~busy[69] ? 69 :
               ~busy[70] ? 70 :
               ~busy[71] ? 71 :
               ~busy[72] ? 72 :
               ~busy[73] ? 73 :
               ~busy[74] ? 74 :
               ~busy[75] ? 75 :
               ~busy[76] ? 76 :
               ~busy[77] ? 77 :
               ~busy[78] ? 78 :
               ~busy[79] ? 79 :
               ~busy[80] ? 80 :
               ~busy[81] ? 81 :
               ~busy[82] ? 82 :
               ~busy[83] ? 83 :
               ~busy[84] ? 84 :
               ~busy[85] ? 85 :
               ~busy[86] ? 86 :
               ~busy[87] ? 87 :
               ~busy[88] ? 88 :
               ~busy[89] ? 89 :
               ~busy[90] ? 90 :
               ~busy[91] ? 91 :
               ~busy[92] ? 92 :
               ~busy[93] ? 93 :
               ~busy[94] ? 94 :
               ~busy[95] ? 95 :
               ~busy[96] ? 96 :
               ~busy[97] ? 97 :
               ~busy[98] ? 98 :
               ~busy[99] ? 99 :
               ~busy[100] ? 100 :
               ~busy[101] ? 101 :
               ~busy[102] ? 102 :
               ~busy[103] ? 103 :
               ~busy[104] ? 104 :
               ~busy[105] ? 105 :
               ~busy[106] ? 106 :
               ~busy[107] ? 107 :
               ~busy[108] ? 108 :
               ~busy[109] ? 109 :
               ~busy[110] ? 110 :
               ~busy[111] ? 111 :
               ~busy[112] ? 112 :
               ~busy[113] ? 113 :
               ~busy[114] ? 114 :
               ~busy[115] ? 115 :
               ~busy[116] ? 116 :
               ~busy[117] ? 117 :
               ~busy[118] ? 118 :
               ~busy[119] ? 119 :
               ~busy[120] ? 120 :
               ~busy[121] ? 121 :
               ~busy[122] ? 122 :
               ~busy[123] ? 123 :
               ~busy[124] ? 124 :
               ~busy[125] ? 125 :
               ~busy[126] ? 126 :
               ~busy[127] ? 127 :
               ~busy[128] ? 128 :
               ~busy[129] ? 129 :
               ~busy[130] ? 130 :
               ~busy[131] ? 131 :
               ~busy[132] ? 132 :
               ~busy[133] ? 133 :
               ~busy[134] ? 134 :
               ~busy[135] ? 135 :
               ~busy[136] ? 136 :
               ~busy[137] ? 137 :
               ~busy[138] ? 138 :
               ~busy[139] ? 139 :
               ~busy[140] ? 140 :
               ~busy[141] ? 141 :
               ~busy[142] ? 142 :
               ~busy[143] ? 143 :
               ~busy[144] ? 144 :
               ~busy[145] ? 145 :
               ~busy[146] ? 146 :
               ~busy[147] ? 147 :
               ~busy[148] ? 148 :
               ~busy[149] ? 149 :
               ~busy[150] ? 150 :
               ~busy[151] ? 151 :
               ~busy[152] ? 152 :
               ~busy[153] ? 153 :
               ~busy[154] ? 154 :
               ~busy[155] ? 155 :
               ~busy[156] ? 156 :
               ~busy[157] ? 157 :
               ~busy[158] ? 158 :
               ~busy[159] ? 159 :
               ~busy[160] ? 160 :
               ~busy[161] ? 161 :
               ~busy[162] ? 162 :
               ~busy[163] ? 163 :
               ~busy[164] ? 164 :
               ~busy[165] ? 165 :
               ~busy[166] ? 166 :
               ~busy[167] ? 167 :
               ~busy[168] ? 168 :
               ~busy[169] ? 169 :
               ~busy[170] ? 170 :
               ~busy[171] ? 171 :
               ~busy[172] ? 172 :
               ~busy[173] ? 173 :
               ~busy[174] ? 174 :
               ~busy[175] ? 175 :
               ~busy[176] ? 176 :
               ~busy[177] ? 177 :
               ~busy[178] ? 178 :
               ~busy[179] ? 179 :
               ~busy[180] ? 180 :
               ~busy[181] ? 181 :
               ~busy[182] ? 182 :
               ~busy[183] ? 183 :
               ~busy[184] ? 184 :
               ~busy[185] ? 185 :
               ~busy[186] ? 186 :
               ~busy[187] ? 187 :
               ~busy[188] ? 188 :
               ~busy[189] ? 189 :
               ~busy[190] ? 190 :
               ~busy[191] ? 191 :
               ~busy[192] ? 192 :
               ~busy[193] ? 193 :
               ~busy[194] ? 194 :
               ~busy[195] ? 195 :
               ~busy[196] ? 196 :
               ~busy[197] ? 197 :
               ~busy[198] ? 198 :
               ~busy[199] ? 199 :
               ~busy[200] ? 200 :
               ~busy[201] ? 201 :
               ~busy[202] ? 202 :
               ~busy[203] ? 203 :
               ~busy[204] ? 204 :
               ~busy[205] ? 205 :
               ~busy[206] ? 206 :
               ~busy[207] ? 207 :
               ~busy[208] ? 208 :
               ~busy[209] ? 209 :
               ~busy[210] ? 210 :
               ~busy[211] ? 211 :
               ~busy[212] ? 212 :
               ~busy[213] ? 213 :
               ~busy[214] ? 214 :
               ~busy[215] ? 215 :
               ~busy[216] ? 216 :
               ~busy[217] ? 217 :
               ~busy[218] ? 218 :
               ~busy[219] ? 219 :
               ~busy[220] ? 220 :
               ~busy[221] ? 221 :
               ~busy[222] ? 222 :
               ~busy[223] ? 223 :
               ~busy[224] ? 224 :
               ~busy[225] ? 225 :
               ~busy[226] ? 226 :
               ~busy[227] ? 227 :
               ~busy[228] ? 228 :
               ~busy[229] ? 229 :
               ~busy[230] ? 230 :
               ~busy[231] ? 231 :
               ~busy[232] ? 232 :
               ~busy[233] ? 233 :
               ~busy[234] ? 234 :
               ~busy[235] ? 235 :
               ~busy[236] ? 236 :
               ~busy[237] ? 237 :
               ~busy[238] ? 238 :
               ~busy[239] ? 239 :
               ~busy[240] ? 240 :
               ~busy[241] ? 241 :
               ~busy[242] ? 242 :
               ~busy[243] ? 243 :
               ~busy[244] ? 244 :
               ~busy[245] ? 245 :
               ~busy[246] ? 246 :
               ~busy[247] ? 247 :
               ~busy[248] ? 248 :
               ~busy[249] ? 249 :
               ~busy[250] ? 250 :
               ~busy[251] ? 251 :
               ~busy[252] ? 252 :
               ~busy[253] ? 253 :
               ~busy[254] ? 254 :
               ~busy[255] ? 255 :
               0;



  always @(posedge clock) begin
    alloc = alloc_raw;
    free = free_raw;
    free_addr = free_addr_raw;
  end
  always @(posedge clock) begin
    count = count + (alloc & ~nack) - (free & busy[free_addr]);
    if (free) busy[free_addr] = 0;
    if (alloc & ~nack) busy[alloc_addr] = 1;
  end

  /*
    // assertions follow

    // definition of when a buffer is freed and allocated

    wire [(`SIZE - 1):0] allocd, freed;
    `for(j = 0; j < `SIZE; j++)
    assign allocd[j] = alloc & ~nack & alloc_addr == `j;
    assign freed[j] = free & free_addr == `j;
    `endfor

    // if an entry is allocated, it is not allocated again until freed

  always
    for(i = 0; i < `SIZE; i = i + 1) begin
      if (allocd[i]) begin
	wait(1);
        while(~freed[i]) begin
          assert safe[i]: ~allocd[i];
          wait(1);
        end
        assert safe[i]: ~allocd[i];
      end
    end
*/

  /*#PASS: count is less than or equal to 16.
count[4]=0 + count[3:0]=0;*/
  //always begin
  wire prop = (count <= (`LOGSIZE+1)'d(`SIZE));
  //end

  wire prop_neg = !prop;
  assume property (alloc_addr <= (`SIZE - 1));
  assume property (free_addr <= (`SIZE - 1));

assume property (@(posedge clock) (alloc & ~nack & $past(busy[alloc_addr])) |-> (free & free_addr == alloc_addr)); 
assert property (prop);

endmodule  // buffer_alloc
