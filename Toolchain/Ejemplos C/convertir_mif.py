import sys  # Importa el modulo para manejar argumentos del sistema

# Verifica si se paso el archivo como argumento
if len(sys.argv) != 2:
    print("Uso: python3 convertir_mif.py <archivo.hex>")  # Mensaje de uso correcto del script
    sys.exit(1)  # Termina el programa si no se proporciona un argumento correcto

hex_filename = sys.argv[1]  # Toma el nombre del archivo .hex del argumento de linea de comandos

# Genera el nombre del archivo .mif a partir del nombre del archivo .hex
mif_filename = hex_filename.replace(".hex", ".mif")

try:
    # Abre el archivo .hex para lectura y el archivo .mif para escritura
    with open(hex_filename, "r") as hex_file, open(mif_filename, "w") as mif_file:
        # Escribe el encabezado del archivo .mif con configuracion estandar
        mif_file.write("WIDTH=32;\nDEPTH=4096;\nADDRESS_RADIX=HEX;\nDATA_RADIX=HEX;\nCONTENT BEGIN\n")
        address = 0  # Inicia el contador de direcciones en 0
        for line in hex_file:
            # Solo procesa las lineas de datos (empiezan con ':')
            if line.startswith(":"):
                # Extrae los datos del registro Intel HEX (datos sin checksum ni direccion)
                data = line[9:-2]
                # Escribe los datos en el formato MIF con direccion formateada
                mif_file.write(f"{address:04X} : {data};\n")
                address += 4  # Incrementa la direccion en 4 para cada linea (32 bits)
        # Escribe el final del archivo .mif
        mif_file.write("END;\n")
        print(f"✅ Archivo {mif_filename} generado correctamente.")  # Mensaje de exito
except FileNotFoundError:
    # Maneja el caso donde el archivo .hex no se encuentra
    print(f"❌ El archivo {hex_filename} no fue encontrado.")
except Exception as e:
    # Maneja cualquier otro error inesperado
    print(f"❌ Error al convertir el archivo: {e}")
