`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06.06.2019 17:22:17
// Design Name: 
// Module Name: top_SIWA_test
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

module top_SIWA_test(
    input        clk,
    input        reset,
	input        boot_init,
	//input [7:0]  data_in,
	//input [15:0] addr,
	input        write,
	input        mode,
	input en_leds,
	output  [7:0] leds,
	input        RX_UART,
	
	output       flash_programmed,
	output       TX_UART

	/*output       boot_init_o,
	output       mode_o,
	output       reset_o,
	output       write_o,
	output       TX_pin*/
	/*output       clk_o,
	output       mosi_o,
	output       miso_o,
	output reg      sclk_o,
	output reg      scs_o,
	output reg  state,
	output [4:0] spi_counter,
	output [2:0] mem_counter,
	output [1:0] byte_count*/
    );
    wire SCS;
    wire SCLK;
    wire MOSI;
    wire MISO;
    wire clk_w;
    
    //wire clk_wire;
    
    pxi_siwa_ifc ifc(
        .clk(clk_w),
        .data_in(8'h00/*data_in*/),
        .addr(16'h0000/*addr*/),
        .ram_write(write),
        .mode(1'b0),
        .reset(~reset),
        .SCS(SCS),
        .SCLK(SCLK),
        .MOSI(MOSI),
        .MISO(MISO),
        .flash_programmed(flash_programmed)/*,
        .state(state),
        .spi_counter_o(spi_counter),
        .mem_counter(mem_counter),
        .byte_count(byte_count)*/
    );
    
    topcore_tecriscv siwa(
        .clk(clk_w),
        .reset(boot_init ),
        .MISO(MISO),
        .RX_UART(RX_UART),
        .maip(1'b0),
        .MOSI(MOSI),
        .SCLK(SCLK),
        .SCS(SCS),
        .TX_UART(TX_UART),
        .full_range_level_shifter(),
        .IS_Val(),
        .IS_Config(),
        .IS_Trigger(),
        .Reg_GPIO_en(),
        .Reg_GPIO_int(8'h00),
        .Reg_GPIO_out()
    );

    clk_wiz_0 clk_gen(//it needs a 100MHz input clk to generate an 20MHz clk output
        .clk_in1(clk),
        .clk_out1(clk_w),
        .reset(reset) // input reset
    );
    
/*    reg mode_r, reset_r, write_r, boot_init_r;

always @(posedge clk) begin
    mode_r      <= mode;
    reset_r     <= reset;
    write_r     <= write;
    boot_init_r <= boot_init;
end

assign mode_o      = mode_r;
assign reset_o     = reset_r;
assign write_o     = write_r;
assign boot_init_o = boot_init_r;*/
    
   /* assign boot_init_o = boot_init;
	assign mode_o = mode;
	assign reset_o = reset;
	assign write_o = write;
	assign TX_pin = TX_UART;*/
	
	/*assign clk_o  = clk_w;
	assign mosi_o = MOSI;
	assign miso_o = MISO;
	assign sclk_o = SCLK;
	assign scs_o  = SCS;*/

endmodule

