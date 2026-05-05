// UART SiFive E en QEMU
#define UART0_BASE   0x10013000UL
#define UART_TXDATA  (*(volatile unsigned int *)(UART0_BASE + 0x00))
#define UART_TXFULL  (1u << 31)

static void uart_putc(char c) {
    // Espera a que haya espacio en el TX FIFO
    while (UART_TXDATA & UART_TXFULL) { }
    UART_TXDATA = (unsigned int)(unsigned char)c;
}

static void uart_print(const char *s) {
    while (*s) uart_putc(*s++);
}

static void uart_print_dec(int v) {
    char buf[16];
    int i = 0, n = v;
    if (n == 0) { uart_putc('0'); return; }
    if (n < 0) { uart_putc('-'); n = -n; }
    while (n > 0 && i < (int)sizeof(buf)) { buf[i++] = '0' + (n % 10); n /= 10; }
    while (i--) uart_putc(buf[i]);
}

int main(void) {
    int a = 12, b = 5, s = a + b;
    uart_print("Resultado de la suma: ");
    uart_print_dec(a); uart_print(" + "); uart_print_dec(b);
    uart_print(" = "); uart_print_dec(s); uart_print("\n");
    while (1) { } // mantener vivo
    return 0;
}
