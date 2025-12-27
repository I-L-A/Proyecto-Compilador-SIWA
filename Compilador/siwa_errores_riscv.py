#-------------------------------------------------------------------------------------------------------------------#
#
#        TECNOLOGICO DE COSTA RICA - TALLER INTEGRADOR GR 20 - 1S 2025
#
#        Codigo para verificar limitaciones y convertir en .hex
#
#-------------------------------------------------------------------------------------------------------------------#

import re  # Importa el módulo de expresiones regulares para buscar patrones en las cadenas de texto
import sys  # Importa el módulo del sistema para interactuar con los argumentos del script
import subprocess  # Importa el módulo para ejecutar comandos del sistema
import os  # Importa el módulo para interactuar con el sistema operativo (archivos y directorios)

# Lista de funciones prohibidas porque requieren librerías estándar no disponibles en el microcontrolador
PROHIBIDAS = ["printf", "scanf", "malloc", "free", "fopen", "fgets", "fprintf"]

# Función que determina si una dirección está dentro de los rangos válidos para TEC-RISC-V
def es_direccion_valida(valor):
    try:
        # Convierte la cadena hexadecimal a un número entero
        direccion = int(valor, 16)
        # Verifica si está dentro del rango de RAM (0x00000000 a 0x00001FFF) 
        # o de los dispositivos IO (0x800000 en adelante)
        return (0x00000000 <= direccion <= 0x00001FFF) or (direccion >= 0x800000)
    except ValueError:
        # Si no es un valor hexadecimal válido, retorna False
        return False

# Función principal que analiza el código fuente .c
def analizar_codigo(archivo):
    errores = []  # Lista para almacenar los errores encontrados
    with open(archivo, 'r') as f:
        # Lee todas las líneas del archivo .c
        lineas = f.readlines()

    # Recorre el código línea por línea
    for num, linea in enumerate(lineas, 1):
        # Verifica si alguna función prohibida está presente en la línea
        for funcion in PROHIBIDAS:
            # Busca la función usando una expresión regular para que sea exacta
            if re.search(rf'\b{funcion}\b', linea):
                errores.append(f"[Línea {num}] ❌ Uso de función prohibida: {funcion}")

        # Verifica si se declara un puntero sin 'volatile'
        if re.search(r'int\s*\*\s*\w+', linea) and "volatile" not in linea:
            errores.append(f"[Línea {num}] ⚠️ Puntero sin 'volatile': {linea.strip()}")

        # Busca direcciones en formato hexadecimal y las verifica
        matches = re.findall(r'0x[0-9a-fA-F]+', linea)
        for match in matches:
            # Verifica si la dirección es válida
            if not es_direccion_valida(match):
                errores.append(f"[Línea {num}] ❌ Dirección no válida: {match}")

        # Verifica si se usa la instrucción 'fence' o 'fence.i' que no son soportadas
        if 'fence' in linea or 'fence.i' in linea:
            errores.append(f"[Línea {num}] ❌ Instrucción no soportada: {linea.strip()}")

        # Verifica si se accede a registros CSR fuera del rango permitido
        if re.search(r'\bcsrr\w*\b', linea):
            match = re.search(r'0x[0-9a-fA-F]+', linea)
            if match:
                direccion = int(match.group(), 16)
                if direccion > 0x07:
                    errores.append(f"[Línea {num}] ❌ CSR fuera del rango permitido: {match.group()}")

    # Imprime los errores encontrados o confirma que el código es compatible
    if errores:
        print("⚠️ Errores encontrados:")
        for err in errores:
            print(err)
    else:
        print("✅ El código parece compatible con TEC-RISC-V.")
        # Si no hay errores, intenta convertir el archivo a formato HEX
        convertir_a_hex(archivo)

# Función para convertir el archivo .c a ensamblador y luego a hexadecimal usando riscv64-unknown-elf-gcc y objcopy
def convertir_a_hex(archivo):
    # Elimina la extensión .c para usarla en los nombres de los archivos de salida
    output_name = archivo.replace('.c', '')
    try:
        # Convertir a ensamblador RISC-V
        print("🔄 Generando ensamblador RISC-V...")
        subprocess.run([
            "riscv64-unknown-elf-gcc", "-march=rv32i", "-mabi=ilp32", "-S", archivo, "-o", f"{output_name}.s"
        ], check=True)
        print(f"✅ Archivo ensamblador generado: {output_name}.s")

        # Generar el archivo ELF
        print("🔄 Compilando a ELF...")
        subprocess.run([
            "riscv64-unknown-elf-gcc", "-march=rv32i", "-mabi=ilp32", "-nostdlib","-T", "linker.ld", "-o", f"{output_name}.elf", f"{output_name}.s"
        ], check=True)
        print(f"✅ Archivo ELF generado: {output_name}.elf")

        # Convertir a HEX
        print("🔄 Generando archivo HEX...")
        subprocess.run([
            "riscv64-unknown-elf-objcopy",  "-O", "ihex", f"{output_name}.elf", f"{output_name}.hex"
        ], check=True)
        print(f"✅ Conversión exitosa: {output_name}.hex")
    except subprocess.CalledProcessError as e:
        # Muestra un error si alguno de los comandos falla
        print(f"❌ Error durante la conversión: {e}")

# Punto de entrada del script
if __name__ == "__main__":
    # Verifica que se pase el archivo .c como argumento
    if len(sys.argv) != 2:
        print("Uso: python siwa_errores_riscv.py archivo.c")
    else:
        # Llama a la función de análisis con el archivo proporcionado
        analizar_codigo(sys.argv[1]) 
