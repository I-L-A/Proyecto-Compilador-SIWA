import re     # Módulo para expresiones regulares (permite buscar patrones en texto)
import sys    # Módulo para trabajar con argumentos desde la línea de comandos

# Lista de funciones prohibidas porque requieren librerías estándar no disponibles en el microcontrolador
PROHIBIDAS = ["printf", "scanf", "malloc", "free", "fopen", "fgets", "fprintf"]

# Función que determina si una dirección está dentro de los rangos válidos para TEC-RISC-V
def es_direccion_valida(valor):
    try:
        direccion = int(valor, 16)  # Convierte la dirección en hexadecimal a entero
        # Verifica si está dentro del rango de RAM o de los dispositivos IO
        return (0x00000000 <= direccion <= 0x00001FFF) or (direccion >= 0x800000)
    except:
        # Si no se puede convertir a entero, retorna False
        return False

# Función principal que analiza el código fuente .c
def analizar_codigo(archivo):
    errores = []  # Lista donde se guardarán los errores encontrados
    with open(archivo, 'r') as f:
        lineas = f.readlines()  # Lee todas las líneas del archivo

    # Recorre el código línea por línea
    for num, linea in enumerate(lineas, 1):
        # Verifica si se usa alguna función prohibida
        for funcion in PROHIBIDAS:
            if re.search(rf'\b{funcion}\b', linea):
                errores.append(f"[Línea {num}] ❌ Uso de función prohibida: {funcion}")

        # Verifica si hay punteros declarados sin la palabra clave 'volatile'
        if re.search(r'int\s*\*\s*\w+', linea) and "volatile" not in linea:
            errores.append(f"[Línea {num}] ⚠️ Puntero sin 'volatile' (posible acceso a IO sin protección): {linea.strip()}")

        # Busca todas las direcciones codificadas en hexadecimal en la línea
        matches = re.findall(r'0x[0-9a-fA-F]+', linea)
        for match in matches:
            if not es_direccion_valida(match):
                errores.append(f"[Línea {num}] ❌ Dirección no válida para este microcontrolador: {match}")

        # Verifica si hay instrucciones 'fence' o 'fence.i' que no están soportadas
        if 'fence' in linea or 'fence.i' in linea:
            errores.append(f"[Línea {num}] ❌ Instrucción no soportada encontrada: {linea.strip()}")

        # Verifica si hay acceso a registros CSR usando código ensamblador
        if re.search(r'\bcsrr\w*\b', linea):  # Busca palabras que empiezan con "csrr"
            match = re.search(r'0x[0-9a-fA-F]+', linea)  # Busca una dirección hexadecimal
            if match:
                direccion = int(match.group(), 16)  # Convierte la dirección a entero
                if direccion > 0x07:  # Solo se permiten CSR con ID entre 0x00 y 0x07
                    errores.append(f"[Línea {num}] ❌ CSR fuera del rango permitido (solo 0x00–0x07): {match.group()}")

    # Muestra los errores encontrados o un mensaje de éxito si todo está bien
    if not errores:
        print("✅ El código parece compatible con TEC-RISC-V.")
    else:
        print("⚠️ Errores encontrados:")
        for err in errores:
            print(err)

# Entrada principal del script: verifica que se pase un archivo como argumento
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python siwa_errores.py archivo.c")  # Mensaje si no se da un archivo
    else:
        analizar_codigo(sys.argv[1])  # Llama a la función con el archivo proporcionado

