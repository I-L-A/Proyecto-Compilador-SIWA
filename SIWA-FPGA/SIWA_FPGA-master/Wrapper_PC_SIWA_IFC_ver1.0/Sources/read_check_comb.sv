`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11.07.2019 04:30:22
// Design Name: 
// Module Name: read_check_comb
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

//this combinational logic checks if the Master send a read signal
module read_check_comb(command, miso_state, mem_read);

    input [7:0] command;
    input       miso_state;
    
    output reg mem_read;
    
    always_comb begin
        if ((command == 8'b00000011) && (miso_state)) mem_read = 1;
        else                                          mem_read = 0;
    end

endmodule
