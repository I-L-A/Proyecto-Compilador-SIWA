`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 18.07.2019 15:32:55
// Design Name: 
// Module Name: hold_reg
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


module hold_reg(clk, reset, trigger, hold);

    input clk;
    input reset;
    input trigger;
    
    output reg hold;
    
    always @ (posedge clk) begin
        if (!reset) hold <= 0;
        else
            if (trigger) begin
                hold <= 1;
            end
            else
                hold <= hold;
    end

endmodule
