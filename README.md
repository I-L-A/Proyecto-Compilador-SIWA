# SIWA Toolchain

Repositorio del entorno de compilación desarrollado para generar programas ejecutables destinados al microcontrolador **SIWA**, una arquitectura basada en **RISC-V RV32I** utilizada en el contexto del proyecto de investigación desarrollado en el **DCI Lab del Tecnológico de Costa Rica (TEC)**.

El objetivo de este repositorio es centralizar las herramientas necesarias para:

- Compilar programas escritos en C
- Generar archivos ejecutables compatibles con la arquitectura SIWA
- Automatizar el flujo de compilación
- Proveer una interfaz gráfica para facilitar el uso del toolchain
- Documentar el funcionamiento del sistema

---

# Estructura del repositorio

El repositorio se encuentra organizado en las siguientes carpetas:

Proyecto-Compilador-SIWA  
│  
├── GUI  
│   ├── SIWA_TOOLCHAIN_GUI.py  
│   └── linker.ld  
│  
├── documentation  
│  
├── examples  
│  
└── README.md  

---

# Carpeta GUI

La carpeta **GUI** contiene la aplicación principal del toolchain.

Dentro de esta carpeta se encuentra la interfaz gráfica desarrollada en Python:

GUI/SIWA_TOOLCHAIN_GUI.py

Esta aplicación permite ejecutar el flujo completo del toolchain de forma automatizada.

Las funciones principales de la herramienta incluyen:

- selección de archivos fuente en C  
- ejecución del compilador RISC-V  
- generación de archivos intermedios  
- generación del archivo final `.hex`  
- validación básica del flujo de compilación  

---

# Linker Script

Dentro de la carpeta **GUI** también se encuentra el archivo:

GUI/linker.ld

Este archivo define el **mapa de memoria utilizado por la arquitectura SIWA**.

El linker script es utilizado durante el proceso de enlazado para generar el ejecutable final compatible con la implementación del procesador.

---

# Flujo de compilación

El toolchain implementa el siguiente flujo de compilación:

Código C  
↓  
riscv64-unknown-elf-gcc  
↓  
Archivo Assembly (.s)  
↓  
Linker  
↓  
Archivo ELF  
↓  
Objcopy  
↓  
Archivo HEX  

El archivo `.hex` generado es el formato utilizado para cargar programas en la memoria del microcontrolador **SIWA**.

---

# Requisitos del sistema

Para utilizar el toolchain es necesario contar con las siguientes herramientas instaladas.

## Python

Versión recomendada:

Python 3.8 o superior

## Toolchain RISC-V

Es necesario instalar el compilador:

riscv64-unknown-elf-gcc

y la herramienta:

riscv64-unknown-elf-objcopy

Estas herramientas permiten generar código compatible con arquitecturas RISC-V.

---

# Ejecución de la interfaz gráfica

Para ejecutar la aplicación gráfica del toolchain se debe ingresar al directorio **GUI** y ejecutar:

python SIWA_TOOLCHAIN_GUI.py

La interfaz gráfica permite:

- seleccionar archivos fuente
- ejecutar el proceso de compilación
- visualizar archivos generados
- producir el archivo `.hex` final

---

# Documentación

El repositorio incluye documentación relacionada con:

- funcionamiento del toolchain  
- instalación del entorno  
- flujo de compilación  
- uso de la interfaz gráfica  

Esta documentación permite reproducir completamente el entorno de desarrollo del proyecto.

---

# Aplicación en el proyecto SIWA

Este toolchain forma parte del proyecto de investigación enfocado en la **caracterización del microcontrolador SIWA**.

El sistema permitirá ejecutar **benchmarks** para analizar métricas de desempeño como:

- CPI (Cycles Per Instruction)
- rendimiento del procesador
- comportamiento del sistema bajo diferentes cargas de trabajo

---

# Laboratorio de desarrollo

Proyecto desarrollado en:

DCI Lab  
Escuela de Ingeniería Electrónica  
Tecnológico de Costa Rica

---

# Estado del proyecto

El proyecto se encuentra en desarrollo activo.

Las líneas actuales de trabajo incluyen:

- mejora del toolchain
- síntesis del SIWA en FPGA
- ejecución de benchmarks
- caracterización del sistema
