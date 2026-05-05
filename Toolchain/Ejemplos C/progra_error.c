#include <stdio.h>
#include <stdlib.h>

#define GPIO_BASE 0x00008000  //  Dirección fuera del rango permitido
#define GPIO (*(unsigned int*)GPIO_BASE)  //  Puntero sin volatile

int main() {
    int a = 25;
    int b = 10;
    int resultado = a + b;

    printf("El resultado es: %d\n", resultado);  //  Función prohibida

    GPIO = resultado;

    __asm__("fence");  //  Instrucción no soportada

    unsigned int val;
    __asm__("csrr %0, 0x300" : "=r"(val));  //  CSR fuera del rango permitido

    return 0;  //  El programa no debe retornar (no hay sistema operativo)
}
