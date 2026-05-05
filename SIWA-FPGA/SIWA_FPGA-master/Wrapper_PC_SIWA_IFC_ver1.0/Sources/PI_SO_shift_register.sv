`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10.07.2019 19:14:16
// Design Name: 
// Module Name: PI_SO_shift_register
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////

//Parallel In - Serial Out 8-bit Shift Register
module PI_SO_shift_register(clk, reset, enable, PI, load, shift, output_en, SO);

    input       clk;
    input       reset;
    input       enable;
    input [7:0] PI;
    input       shift;
    input       load;
    input       output_en;
    
    output      SO;
    
    reg [7:0] shft_reg;
    reg       out_reg;
    
    always @ (posedge clk) begin
        if      (!reset) begin
            shft_reg <= 0;
            out_reg  <= 0;
        end
        else if (load)      shft_reg <= PI;
        else if (shift)     shft_reg <= {shft_reg[6:0],1'b0};
        else                shft_reg <= shft_reg;
        out_reg <= (output_en) ? shft_reg[7] : out_reg;
    end

    assign SO = (enable) ? out_reg : 1'bz;
    
endmodule
