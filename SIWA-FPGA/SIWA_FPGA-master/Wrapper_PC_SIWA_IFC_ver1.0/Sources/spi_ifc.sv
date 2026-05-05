`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 05.06.2019 14:42:56
// Design Name: 
// Module Name: spi_ifc
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

//This module is a 2-state FSM that communicates with SIWA through the SPI ifc
module spi_ifc(clk, reset, SCS, SCLK_r, SCLK_f, mode, /*control_rst,*/ mosi_check, mosi_shift,
               mosi_count, in_cnt, miso_check, miso_shift, miso_count, /*miso_read, */byte_check, shft_cnt,
               spi_count_init, mem_count_init, miso_en, output_en, master_read/*, state*/);
  
  input         clk;
  input         reset;
  input 	    SCS;
  input         SCLK_r;
  input         SCLK_f;
  input         mode; //0: flash emulation; 1: writting flash mem
  input         mosi_check;
  input [5:0]   in_cnt;
  input         miso_check;
  input         byte_check;
  input [2:0]   shft_cnt;
  input         spi_count_init;
  input         mem_count_init;
  
  //output reg    control_rst;
  output reg    mosi_shift;
  output reg    mosi_count;
  output reg    miso_shift;
  output reg    miso_count;
  //output reg [15:0] spi_addr;
  //output reg    miso_read;
  output reg    miso_en;
  output reg    output_en;
  output reg    master_read;
  
  //output state;
  
  reg next_state;
  reg state;
  //reg spi_count_init;
  //reg mem_count_init;
  reg mem_count_inc;
  
  parameter MOSI_MODE = 0;
  parameter MISO_MODE = 1;
  
  //next_state combinational logic
  
  always_comb /*(mode,SCS,reset,SCLK_r,SCLK_f,state,spi_counter,mem_counter,byte_count)*/ begin
      case(state)
          MOSI_MODE: begin
              if (mode == 0) begin
                  next_state = (mosi_check) ? MISO_MODE : MOSI_MODE;
              end
         end
         MISO_MODE: begin
              if (mode == 0) begin
                  next_state = (miso_check) ? MOSI_MODE : MISO_MODE;
              end
          end
      endcase
  end
 
  //output logic and internal registers combinational logic 
  
  always_comb begin
      if ((SCS) || (!reset)) begin
          mosi_shift = 0;
          mosi_count = 0;
          miso_shift = 0;
          miso_count = 0;
          //miso_read = 0;
          //spi_count_init = 0;
          //mem_count_init = 0;
          mem_count_inc = 1;
          //control_rst = 0;
          miso_en = 0;
          output_en = 0;
          master_read = 0;
      end
      else if ((!SCS) && (reset) && (SCLK_r)) begin
          case(state)
              MOSI_MODE: begin
                      mosi_shift = 1;
                      miso_shift = 0;
                      miso_count = 0;
                      //miso_read = 1;
                      //spi_count_init = 1;
                      //mem_count_init = 0;
                      mem_count_inc = 1;
                      if (in_cnt > 30) miso_en = 1;
                      output_en = (in_cnt > 30) ? 1 : 0;
                      master_read = (in_cnt == 30) ? 1 : 0;
                      //control_rst = 1;
              end
              MISO_MODE: begin
                      mosi_shift = 0;
                      mosi_count = 0;
                      miso_en = 1;
                      //spi_count_init  = 0;
                      //mem_count_init  = 1;
                      miso_shift = 1;//(mem_count_inc) ? 1 : 0;
                      //miso_read  = (mem_count_inc) ? 0 : 1;
                      master_read = 0;
                      //control_rst = 1;
              end
          endcase
      end
      else if ((!SCS) && (reset) && (SCLK_f)) begin
          case(state)
              MOSI_MODE: begin
                      miso_shift = 0;
                      miso_count = 0;
                      //miso_read = 1;
                      //mem_count_init = 0;
                      mem_count_inc = 1;
                      if (in_cnt > 30) miso_en = 1;
                      output_en = (in_cnt > 30) ? 1 : 0;
                      mosi_count = (spi_count_init) ? 1 : 0;
                      master_read = 0;
                      //control_rst = 1;
                      
              end
              MISO_MODE: begin
                      mosi_shift = 0;
                      mosi_count = 0;
                      //spi_count_init = 0;
                      mem_count_inc = (shft_cnt < 7) ? 1 : 0;
                      miso_en = 1;//(mem_count_init) ? 1 : 0;
                      output_en = (mem_count_init) ? 1 : 0;
                      master_read = 0;
                      //control_rst = 1;
              end
          endcase
      end
      else begin
          mosi_shift = 0;
          mosi_count = 0;
          miso_shift = 0;
          miso_count = 0;
          //miso_read = 0;
          output_en = 0;
          master_read = 0;
          if (byte_check) mem_count_inc = 0;
      end
  end
  
  //state change sequential logic
  
  always @ (posedge clk) begin
      if ((SCS) || (!reset)) begin
          state <= MOSI_MODE;
      end
      else begin
          state <= next_state;
      end
  end
  
endmodule
