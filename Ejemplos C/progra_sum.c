#define GPIO_BASE 0x80000000
#define GPIO (*(volatile unsigned int*)GPIO_BASE)



volatile int a = 12;
volatile int b = 5;
volatile int resultado;

void main() {
    // Realiza la suma
    resultado = a + b;

    // Muestra el resultado en el GPIO (por ejemplo, LEDs)
    GPIO = resultado;

    // Bucle infinito para mantener el resultado visible
    while (1);
}

