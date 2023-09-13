module ecc_11to16(
  input   logic  [10:0]  enc_in,
  output  logic  [15:0]  enc_out,
  input   logic  [15:0]  dec_in,
  output  logic  [10:0]  dec_out,
  output  logic           err_correct,
  output  logic           err_uncorrect,
  output  logic  [3:0]  err_location
);

//- ECC Encode Logic
assign enc_out[0] = enc_in[0] ^ enc_in[1] ^ enc_in[3] ^ enc_in[4] ^ enc_in[6] ^ enc_in[8] ^ enc_in[10];
assign enc_out[1] = enc_in[0] ^ enc_in[2] ^ enc_in[3] ^ enc_in[5] ^ enc_in[6] ^ enc_in[9] ^ enc_in[10];
assign enc_out[2] = enc_in[0];
assign enc_out[3] = enc_in[1] ^ enc_in[2] ^ enc_in[3] ^ enc_in[7] ^ enc_in[8] ^ enc_in[9] ^ enc_in[10];
assign enc_out[4] = enc_in[1];
assign enc_out[5] = enc_in[2];
assign enc_out[6] = enc_in[3];
assign enc_out[7] = enc_in[4] ^ enc_in[5] ^ enc_in[6] ^ enc_in[7] ^ enc_in[8] ^ enc_in[9] ^ enc_in[10];
assign enc_out[8] = enc_in[4];
assign enc_out[9] = enc_in[5];
assign enc_out[10] = enc_in[6];
assign enc_out[11] = enc_in[7];
assign enc_out[12] = enc_in[8];
assign enc_out[13] = enc_in[9];
assign enc_out[14] = enc_in[10];
assign enc_out[15] = enc_in[0] ^ enc_in[1] ^ enc_in[2] ^ enc_in[4] ^ enc_in[5] ^ enc_in[7] ^ enc_in[10];

//- ECC Decode Logic
//  Decode Raw Data
logic [10:0] dec_raw;
assign dec_raw = {dec_in[14],dec_in[13],dec_in[12],dec_in[11],dec_in[10],dec_in[9],dec_in[8],dec_in[6],dec_in[5],dec_in[4],dec_in[2]};

//  Syndrome Logic
logic [4:0] syndrome;
assign syndrome[0] = dec_in[0] ^ dec_in[2] ^ dec_in[4] ^ dec_in[6] ^ dec_in[8] ^ dec_in[10] ^ dec_in[12] ^ dec_in[14];
assign syndrome[1] = dec_in[1] ^ dec_in[2] ^ dec_in[5] ^ dec_in[6] ^ dec_in[9] ^ dec_in[10] ^ dec_in[13] ^ dec_in[14];
assign syndrome[2] = dec_in[3] ^ dec_in[4] ^ dec_in[5] ^ dec_in[6] ^ dec_in[11] ^ dec_in[12] ^ dec_in[13] ^ dec_in[14];
assign syndrome[3] = dec_in[7] ^ dec_in[8] ^ dec_in[9] ^ dec_in[10] ^ dec_in[11] ^ dec_in[12] ^ dec_in[13] ^ dec_in[14];
assign syndrome[4] = dec_in[0] ^ dec_in[1] ^ dec_in[2] ^ dec_in[3] ^ dec_in[4] ^ dec_in[5] ^ dec_in[6] ^ dec_in[7] ^ dec_in[8] ^ dec_in[9] ^ dec_in[10] ^ dec_in[11] ^ dec_in[12] ^ dec_in[13] ^ dec_in[14] ^ dec_in[15];

//  Decode Data output
logic [15:0] ecc_xor;
assign ecc_xor = 1'b1 << {!syndrome[4], syndrome[3:0]};
logic [10:0] dec_xor;
assign dec_xor = {ecc_xor[15],ecc_xor[14],ecc_xor[13],ecc_xor[12],ecc_xor[11],ecc_xor[10],ecc_xor[9],ecc_xor[7],ecc_xor[6],ecc_xor[5],ecc_xor[3]};
assign dec_out = dec_raw ^ dec_xor;

//  Decode Error message
assign err_correct = syndrome[4];
assign err_uncorrect = (!syndrome[4]) & (|syndrome[3:0]);
assign err_location = syndrome[3:0]-1;

endmodule
