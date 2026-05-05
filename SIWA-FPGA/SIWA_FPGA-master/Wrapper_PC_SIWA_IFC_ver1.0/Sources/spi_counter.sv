`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11.07.2019 04:03:38
// Design Name: 
// Module Name: spi_counter
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


module spi_counter #(parameter BITS = 5,
                     parameter CHECK_VALUE = 0)
                     (clk,reset,count,check,count_o);

    input clk;
    input reset;
    input count;
    
    output reg check;
    output [(BITS-1):0] count_o;
    
    reg [(BITS-1):0] tmp;
    
    localparam MAX_LIMIT = (CHECK_VALUE == 0) ? ((2 ** BITS) - 1) : CHECK_VALUE;
    
    always @ (posedge clk) begin
        if (!reset) begin
            tmp   <= 0;
            check <= 0;
        end
        else if (count) begin
            tmp <= tmp + 1;
            check <= (tmp == MAX_LIMIT) ? 1 : 0;
        end
        else check <= 0;
    end
    
    assign count_o = tmp;

endmodule
