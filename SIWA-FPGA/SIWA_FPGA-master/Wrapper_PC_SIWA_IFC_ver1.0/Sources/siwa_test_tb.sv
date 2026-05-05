`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 07.06.2019 13:38:34
// Design Name: 
// Module Name: siwa_test_tb
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


module siwa_test_tb();
    
  reg        clk;
  reg        reset;
  reg        boot_init;
  reg [7:0]  data_in;
  reg [15:0] addr;
  reg 		 ram_write;
  reg 		 mode;
  reg		 TX_UART;
  
  wire		 RX_UART;
  wire      flash_programmed;
  wire      boot_init_o;
  wire      mode_o;
  wire      reset_o;
  wire      ram_write_o;
  wire      TX_pin;
  /*wire clk_o;
  wire miso;
  wire mosi;
  wire sclk;
  wire scs;
  wire state;
  wire [4:0] spi_counter;
  wire [2:0] mem_counter;
  wire [1:0] byte_count;*/
  
  logic finish;
  logic [6:0] counter;
  
  top_SIWA_test dut(
    .clk(clk),
    .reset(reset),
    .boot_init(boot_init),
   // .data_in(data_in),
    //.addr(addr),
    .write(ram_write),
    .mode(mode),
    .RX_UART(TX_UART),
    .TX_UART(RX_UART),
    .flash_programmed(flash_programmed),
    .boot_init_o(boot_init_o),
    .mode_o(mode_o),
    .reset_o(reset_o),
    .write_o(ram_write_o),
    .TX_pin()/*,
    .clk_o(clk_o),
    .mosi_o(mosi),
    .miso_o(miso),
    .sclk_o(sclk),
    .scs_o(scs),
    .state(state),
    .spi_counter(spi_counter),
    .mem_counter(mem_counter),
    .byte_count(byte_count)*/
  );
  
  initial begin
    $dumpfile("dump.vcd");
  	$dumpvars;
    
    data_in = 0;
    addr = 0;
    ram_write = 0;
    mode = 0;
    finish = 0;
    counter = 0;
    boot_init = 1;
    clk = 0;
    reset = 1;
    TX_UART = 1;
    /*
    #5
    data_in = 8'h26;
    ram_write = 1;
    addr = 0;
    
    #5
    data_in = 8'h04;
    ram_write = 1;
    addr = 1;
    
    #5
    data_in = 8'h47;
    ram_write = 1;
    addr = 2;
    
    #5
    data_in = 8'h0F;
    ram_write = 1;
    addr = 3;
    
    #5
    data_in = 8'hFF;
    ram_write = 1;
    addr = 4;
    
    #5
    data_in = 8'hFE;
    ram_write = 1;
    addr = 5;
    
    #5
    data_in = 8'h7F;
    ram_write = 1;
    addr = 6;
    
    #5
    data_in = 8'hFF;
    ram_write = 1;
    addr = 7;
    
    #5
    data_in = 8'h00;
    ram_write = 1;
    addr = 8;
    
    #5
    data_in = 8'h01;
    ram_write = 1;
    addr = 9;
    
    #5
    data_in = 8'h80;
    ram_write = 1;
    addr = 10;
    
    #5
    data_in = 8'h00;
    ram_write = 1;
    addr = 11;
    
    #5
    ram_write = 0;
    */
    
    #10
    reset = 0;
    
    #20
    reset = 1;
    
    #50
    boot_init = 0;
    
    //#10000000
    //$finish;
    
  end
  
  always begin
    #5 clk = !clk;
  end
  
endmodule
