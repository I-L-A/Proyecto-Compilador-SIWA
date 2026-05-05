ENTRY(main)  # Define el punto de entrada del programa (start)

MEMORY {  # Definición de las regiones de memoria para código, datos y periféricos
CODE (rx)  : ORIGIN = 0x00000000, LENGTH = 4K  # Región para el código ejecutable (4 KB desde 0x00000000)
DATA (rw)  : ORIGIN = 0x00001000, LENGTH = 4K  # Región para datos inicializados y no inicializados (4 KB desde 0x00001000)
UART (rw)  : ORIGIN = 0x0080000, LENGTH = 8M  # Región para UART (8 MB desde 0x0080000)
SPI  (rw)  : ORIGIN = 0x0100000, LENGTH = 16M  # Región para SPI (16 MB desde 0x0100000)
}

SECTIONS {  # Definición de las secciones del archivo ejecutable (.text, .data, .bss)
.text : {  # Sección de código ejecutable y datos de solo lectura
*(.text*)  # Sección de código ejecutable y datos de solo lectura
*(.init)
*(.rodata*)
KEEP(*(.startup*)) # Asegura que las secciones de arranque no sean eliminadas durante la optimización
} > CODE  # Región para el código ejecutable (4 KB desde 0x00000000)


.data : {  # Sección para datos inicializados
*(.data*)  # Sección para datos inicializados
} > DATA  # Región para datos inicializados y no inicializados (4 KB desde 0x00001000)

.bss : {  # Sección para datos no inicializados (variables globales sin valor inicial)
*(.bss*)  # Sección para datos no inicializados (variables globales sin valor inicial)
*(COMMON)
} > DATA  # Región para datos inicializados y no inicializados (4 KB desde 0x00001000)

.uart : {  # Sección para datos relacionados con UART
*(.uart*)  # Sección para datos relacionados con UART
} > UART  # Región para UART (8 MB desde 0x0080000)

.spi : {  # Sección para datos relacionados con SPI
*(.spi*)  # Sección para datos relacionados con SPI
} > SPI  # Región para SPI (16 MB desde 0x0100000)
}
