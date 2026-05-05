`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 05.06.2019 14:38:21
// Design Name: 
// Module Name: pxi_siwa_ifc
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


module pxi_siwa_ifc(
    
  input        clk,
  input [7:0]  data_in,
  input [15:0] addr,
  input	       ram_write,
  input        mode, //0: flash emulation, 1: read/write flash
  input        reset,
  input        SCS,
  input        SCLK,
  input        MOSI,
  
  output       MISO,
  output       flash_programmed/*,
  output state,
  output [5:0] spi_counter_o,
  output [2:0] mem_counter,
  output [1:0] byte_count,
  
  //
  output reg sclk_r,
  output reg sclk_f,
  output reg control_rst,
  output reg mosi_check,
  output reg mosi_shift,
  output reg mosi_count,
  output reg miso_check,
  output reg miso_shift,
  output reg miso_count,
  output reg miso_read,
  output reg byte_check,
  output reg [31:0] mosi_pkt,
  output reg miso_en,
  output reg output_en,
  output reg master_read*/
  //
  
  );
  
  wire [7:0]  spi_data;
  wire        spi_read;
  wire [15:0] spi_addr;
  wire        sclk_r;
  wire        sclk_f;
  wire        mosi_check;
  wire        mosi_shift;
  wire        mosi_count;
  wire        miso_check;
  wire        miso_shift;
  wire        miso_count;
  wire        byte_check;
  wire [31:0] mosi_pkt;
  wire        miso_en;
  wire        output_en;
  wire        master_read;
  wire       spi_cnt_init;
  wire       mem_cnt_init;
  wire [5:0] spi_counter_o;
  wire [2:0] mem_counter;
  wire [1:0] byte_count;
  
  reg rst_3_bit_cntr;
  reg mem_read;
  reg [15:0] mem_addr;
  reg [7:0]  command;
  reg mem_cnt;
  reg read;
  reg control_rst;
  reg miso_read;
  
  pxi_spi_memory RAM (
    .clk(clk),
    .data_in(data_in),
    .addr(addr),
    .write(ram_write),
    .spi_addr(spi_addr),
    //.spi_read(mem_read),
    .spi_read(spi_read),
    .data_out(spi_data),
    .flash_programmed(flash_programmed)
  );
  
  spi_ifc SPI_FSM (
    .clk(clk),
    .reset(reset),
    .SCS(SCS),
    .SCLK_r(sclk_r),
    .SCLK_f(sclk_f),
    .mode(mode),
    //.control_rst(control_rst),
    .mosi_check(mosi_check),
    .mosi_shift(mosi_shift),
    .mosi_count(mosi_count),
    .in_cnt(spi_counter_o),
    .miso_check(miso_check),
    .miso_shift(miso_shift),
    .miso_count(miso_count),
    //.miso_read(miso_read),
    .byte_check(byte_check),
    .shft_cnt(mem_counter),
    .spi_count_init(spi_cnt_init),
    .mem_count_init(mem_cnt_init),
    .miso_en(miso_en),
    .output_en(output_en),
    .master_read(master_read)//,
    //.state(state)
  );
  
  edge_detection sclk_edge_detection (
    .async_sig(SCLK),
    .clk(clk),
    .reset(reset),
    .rise(sclk_r),
    .fall(sclk_f)
  );
  
  PI_SO_shift_register SPI_out_reg (
    .clk(clk),
    .reset(control_rst),
    .enable(miso_en),
    .PI(spi_data),
    .shift(miso_shift),
    .load(mem_read),
    .output_en(output_en),
    .SO(MISO)
  );
  
  SI_PO_shift_register SPI_in_reg (
    .clk(clk),
    .reset(control_rst),
    .SI(MOSI),
    .shift(mosi_shift),
    .index(spi_counter_o[4:0]),
    .PO(mosi_pkt)
  );
  
  spi_counter #(.BITS(6),.CHECK_VALUE(31)) counter_5_bit (
    .clk(clk),
    .reset(control_rst),
    .count(mosi_count),
    .check(mosi_check),
    .count_o(spi_counter_o)
  );
  
  spi_counter #(.BITS(3),.CHECK_VALUE(6)) counter_3_bit (
    .clk(clk),
    .reset(rst_3_bit_cntr),
    .count(mem_cnt),
    .check(byte_check),
    .count_o(mem_counter)
  );
  
  spi_counter #(.BITS(2)) counter_2_bit (
    .clk(clk),
    .reset(control_rst),
    .count(byte_check),
    .check(miso_check),
    .count_o(byte_count)
  );
  
  read_check_comb read_check_logic (
    .command(mosi_pkt[31:24]),
    //.miso_state(miso_read),
    .miso_state(mem_read),
    .mem_read(spi_read)
  );
  
  addr_calc_comb addr_calc (
    .init_addr(mosi_pkt[15:0]),
    .offset(byte_count),
    .final_addr(spi_addr)
  );
  
  hold_reg spi_init_flg(
    .clk(clk),
    .reset(control_rst),
    .trigger(sclk_r),
    .hold(spi_cnt_init)
  );
  
  hold_reg mem_init_flg(
    .clk(clk),
    .reset(control_rst),
    .trigger(sclk_r),
    .hold(mem_cnt_init)
  );
  
  assign control_rst = !(!reset || SCS);
  assign rst_3_bit_cntr = (control_rst && !spi_read);
  //assign mem_read = (master_read) ? master_read : (spi_read);
  assign mem_read = (master_read) ? master_read : (miso_read);
  assign mem_cnt = (miso_shift) && !(mem_counter[2] && mem_counter[1] && mem_counter[0]);
  assign miso_read = (miso_shift) && (mem_counter[2] && mem_counter[1] && mem_counter[0]);
  
endmodule
