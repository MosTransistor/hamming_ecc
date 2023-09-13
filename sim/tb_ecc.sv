`timescale 1ns/1ps

module tb_ecc();

    initial begin
        $dumpfile("ecc.vcd");
        $dumpvars(0, tb_ecc);
    end
    
    logic t_clk=0;
    always #5 t_clk = ~t_clk;

    logic [10:0] e_in;
    logic [15:0] mid;
    logic [15:0] mid_xor;
    logic [10:0] d_out;
    integer      ecc_flag=0;
    logic [15:0] err_position=0;
    logic [15:0] ext_position=0;
    logic [3:0]  position;
    logic        correct;
    logic        uncorrect;

    initial begin
        $display("\033[30;42m --- simulation begin \033[0m");
        repeat (5000) begin
            repeat (1) @(posedge t_clk);
            ecc_flag = $urandom_range(2);
            err_position = $urandom_range(0, 15);
            ext_position = $urandom_range(0, 15);
            e_in = $urandom;
        end
        repeat (2) @(posedge t_clk);
        $display("\033[30;42m [PASS] simulation pass!!! \033[0m");
        $finish;
    end   

    always begin
        #1ps;
        if (err_position === ext_position) begin
            ext_position = $urandom_range(0, 15);
        end
    end
    
    always @(*) begin
        case(ecc_flag)
            0: mid_xor = mid; 
            1: mid_xor = mid ^ (1'b1 << err_position);
            2: mid_xor = mid ^ (1'b1 << err_position) ^ (1'b1 << ext_position);
        endcase
    end

    // monitor
    always @(negedge t_clk) begin
        case(ecc_flag)
            0: begin
                if ((e_in !== d_out) || (correct === 1) || (uncorrect === 1)) begin
                    $display("\033[30;41m [Error] no error inject mode, enc_in = %h, dec_out = %h, err_correct = %h, err_uncorrect = %h \033[0m", e_in,d_out,correct,uncorrect);
                    $stop;
                end
            end
            1: begin
                if ((e_in !== d_out) || (correct !== 1) || (uncorrect === 1) || (position !== err_position)) begin
                    $display("\033[30;41m [Error] error inject 1-bit mode, enc_in = %h, dec_out = %h, err_correct = %h, err_uncorrect = %h \033[0m", e_in,d_out,correct,uncorrect);
                    $display("\033[30;41m [Error] error inject 1-bit mode, err_location == %h, inj_location == %h \033[0m", position, err_position);
                    $stop;
                end
            end
            2: begin
                if ((correct === 1) || (uncorrect !== 1)) begin
                    $display("\033[30;41m [Error] error inject 2-bit mode, err_correct = %h, err_uncorrect = %h \033[0m",correct,uncorrect);
                    $stop;
                end
            end
        endcase
    end

    ecc_11to16  i_ecc_test(.enc_in(e_in), .enc_out(mid), .dec_in(mid_xor), .dec_out(d_out), .err_correct(correct), .err_uncorrect(uncorrect), .err_location(position));

endmodule