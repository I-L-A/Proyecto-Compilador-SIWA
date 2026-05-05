`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 05.06.2019 14:41:26
// Design Name: 
// Module Name: pxi_spi_memory
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


module pxi_spi_memory(clk,data_in, addr, write, spi_addr, spi_read, data_out, flash_programmed);
    
  input        clk;
  input [7:0]  data_in;
  input [15:0] addr;
  input 	   write;
  input [15:0] spi_addr;
  input 	   spi_read;
  output [7:0] data_out;
  output       flash_programmed;
  
  reg [7:0] mem [0:511];
  reg flash_programmed = 0;
  
  initial begin
    mem[0] = 8'h13;
    mem[1] = 8'h01;
    mem[2] = 8'h00;
    mem[3] = 8'h40;
    
    mem[4] = 8'h73;
    mem[5] = 8'h50;
    mem[6] = 8'h5a;
    mem[7] = 8'h00;
    
    mem[8] = 8'h73;
    mem[9] = 8'hd0;
    mem[10] = 8'h6f;
    mem[11] = 8'h00;
    
    mem[12] = 8'h73;
    mem[13] = 8'h60;
    mem[14] = 8'h01;
    mem[15] = 8'h00;
    
    mem[16] = 8'h6f;
    mem[17] = 8'h00;
    mem[18] = 8'h80;
    mem[19] = 8'h00;
    
    mem[20] = 8'h13;
    mem[21] = 8'h01;
    mem[22] = 8'h01;
    mem[23] = 8'hf8;
    
    mem[24] = 8'h13; //addi
    mem[25] = 8'h04;
    mem[26] = 8'h34;
    mem[27] = 8'h24;
    
    mem[28] = 8'h13; //slli
    mem[29] = 8'h14;
    mem[30] = 8'hb4;
    mem[31] = 8'h00;
    
    mem[32] = 8'h13; //addi
    mem[33] = 8'h04;
    mem[34] = 8'hb4;
    mem[35] = 8'h15;
    
    mem[36] = 8'h13; //slli
    mem[37] = 8'h14;
    mem[38] = 8'ha4;
    mem[39] = 8'h00;
    
    mem[40] = 8'h13; //addi
    mem[41] = 8'h04;
    mem[42] = 8'hc4;
    mem[43] = 8'h06;
    
    /*mem[24] = 8'h37; //LUI on register x8
    mem[25] = 8'h04; //the msb bits are uart_data [15:12]
    mem[26] = 8'h65; //uart_data[23:16]    
    mem[27] = 8'h48; //uart_data[31:24]
       
    mem[28] = 8'h13;
    mem[29] = 8'h04;
    mem[30] = 8'hc4; //the msb bits are uart_data [3:0]
    mem[31] = 8'hc6; //uart_data[11:4]*/
      
    mem[44] = 8'hb7; //lui
    mem[45] = 8'h94;
    mem[46] = 8'h98;
    mem[47] = 8'h00; 
       
    mem[48] = 8'h93;
    mem[49] = 8'h84;
    mem[50] = 8'h04;
    mem[51] = 8'h68;  
      
    mem[52] = 8'h23;
    mem[53] = 8'ha0;
    mem[54] = 8'h84;
    mem[55] = 8'h00; 
       
    mem[56] = 8'h6f;
    mem[57] = 8'h00;
    mem[58] = 8'h00;
    mem[59] = 8'h00;
    
    mem[60] = 8'hff;
    mem[61] = 8'hff;
    mem[62] = 8'hff;
    mem[63] = 8'hff;
  end

  assign data_out = (spi_read) ? mem[spi_addr] : {8{1'bz}};
  
  always @ (posedge clk) begin
    if (write) begin
        mem[addr] = data_in;
        flash_programmed = 1;
    end
  end
    
endmodule
