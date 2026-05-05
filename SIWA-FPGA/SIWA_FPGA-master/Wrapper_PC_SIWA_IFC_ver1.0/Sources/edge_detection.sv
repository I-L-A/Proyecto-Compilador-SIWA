`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 27.06.2019 14:47:47
// Design Name: 
// Module Name: edge_detection
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


module edge_detection (input async_sig,
                       input clk,
                       input reset,
                       output reg rise,
                       output reg fall/*,
                       output [2:0] resync_o*/);

  reg [2:0] resync;

  always @(posedge clk) begin
    if (!reset) begin
        resync <= {async_sig,async_sig,async_sig};
        rise   <= 0;
        fall   <= 0;
    end
    else begin// detect rising and falling edges.
        rise <= resync[1] & !resync[0];
        fall <= resync[0] & !resync[1];
        // update history shifter.
        resync <= {async_sig , resync[2:1]};
    end
  end
  
  //assign resync_o = resync;

endmodule
