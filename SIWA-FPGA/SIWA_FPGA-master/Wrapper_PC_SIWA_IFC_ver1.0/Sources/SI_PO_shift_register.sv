`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10.07.2019 18:56:18
// Design Name: 
// Module Name: SI_PO_shift_register
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

//Serial In - Parallel Out 32-bit Shift Register
module SI_PO_shift_register(clk, reset, SI, shift, index, PO);

    input         clk;
    input         reset;
    input         SI;
    input         shift;
    input [4:0]   index;
    
    output [31:0] PO;
    
    reg [31:0] shft_reg;
    
    always @ (posedge clk) begin
        if      (!reset) shft_reg <= 0;
        else if (shift)  shft_reg[31-index] <= SI;
        else             shft_reg <= shft_reg;
    end
    
    assign PO = shft_reg;

endmodule