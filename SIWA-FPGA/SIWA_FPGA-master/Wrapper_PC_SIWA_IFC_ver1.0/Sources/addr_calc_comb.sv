`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11.07.2019 07:55:02
// Design Name: 
// Module Name: addr_calc_comb
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


module addr_calc_comb(init_addr, offset, final_addr);

    input [15:0] init_addr;
    input [1:0]  offset;
    
    output reg [15:0] final_addr;
    
    always_comb final_addr = init_addr + {14'd0,offset};

endmodule
