#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SIWA ERRORES GUI — TEC-RISC-V (RV32I)
Autor: Iván 
Descripción: GUI para analizar código C y generar .s, .elf, .hex y .bin para TEC-RISC-V (RV32I)
Requisitos:
  - Python 3.x
  - Toolchain RISC-V en PATH (riscv64-unknown-elf-gcc / objcopy)
  - (Opcional) QEMU para ejecutar: qemu-system-riscv32
"""

import os
import re
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from shutil import which

# ========= Reglas de análisis =========
PROHIBIDAS = ["printf", "scanf", "malloc", "free", "fopen", "fgets", "fprintf"]

def es_direccion_valida(valor: str) -> bool:
    """
    Acepta:
      - RAM baja: 0x00000000 .. 0x00001FFF
      - I/O / mapeos altos (dos convenciones vistas en doc/ejemplos): >= 0x00800000 o >= 0x80000000
    """
    try:
        direccion = int(valor, 16)
        return (0x00000000 <= direccion <= 0x00001FFF) or (direccion >= 0x00800000) or (direccion >= 0x80000000)
    except ValueError:
        return False

def analizar_codigo(path_c: str) -> list[str]:
    errores = []
    with open(path_c, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    for num, linea in enumerate(lineas, 1):
        for funcion in PROHIBIDAS:
            if re.search(rf"\b{funcion}\b", linea):
                errores.append(f"[Línea {num}] ❌ Uso de función prohibida: {funcion}")

        if re.search(r"\bint\s*\*\s*\w+", linea) and "volatile" not in linea:
            errores.append(f"[Línea {num}] ⚠️ Puntero sin 'volatile': {linea.strip()}")

        matches = re.findall(r"0x[0-9a-fA-F]+", linea)
        for match in matches:
            if not es_direccion_valida(match):
                errores.append(f"[Línea {num}] ❌ Dirección no válida: {match}")

        if "fence.i" in linea or re.search(r"\bfence\b", linea):
            errores.append(f"[Línea {num}] ❌ Instrucción no soportada: {linea.strip()}")

        if re.search(r"\bcsrr\w*\b", linea):
            m = re.search(r"0x[0-9a-fA-F]+", linea)
            if m and int(m.group(), 16) > 0x07:
                errores.append(f"[Línea {num}] ❌ CSR fuera del rango permitido: {m.group()}")

    return errores

# ========= Utilidades =========
def run_cmd(cmd: list[str]) -> tuple[int, str]:
    """Ejecuta un comando y devuelve (returncode, salida_combined)."""
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
        return p.returncode, p.stdout
    except FileNotFoundError:
        return 127, f"❌ Comando no encontrado: {cmd[0]}\nAsegúrate de que esté en el PATH."

def base_sin_ext(path: str) -> str:
    return os.path.splitext(path)[0]

def exists_in_path(exe: str) -> bool:
    return which(exe) is not None

# ========= GUI =========
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SIWA TOOLCAHIN GUI — TEC-RISC-V")
        self.geometry("880x700")

        # Estado
        self.path_c = tk.StringVar()
        self.path_linker = tk.StringVar()
        self.march = tk.StringVar(value="rv32i")
        self.mabi = tk.StringVar(value="ilp32")
        self.tool_prefix = tk.StringVar(value="riscv64-unknown-elf-")
        self.addr_text = tk.StringVar(value="0x00000000")  # fallback .text

        # Opciones de salida
        self.want_s = tk.BooleanVar(value=True)
        self.want_elf = tk.BooleanVar(value=True)
        self.want_hex = tk.BooleanVar(value=True)
        self.want_bin = tk.BooleanVar(value=True)

        # UI
        self._build_ui()

        # Atajo de teclado para limpiar consola
        self.bind_all("<Control-l>", lambda e: self.on_clear_log())

    def _build_ui(self):
        pad = {"padx": 8, "pady": 6}

        # Archivo C
        tk.Label(self, text="Archivo .c:").grid(row=0, column=0, sticky="e", **pad)
        tk.Entry(self, textvariable=self.path_c, width=72).grid(row=0, column=1, **pad)
        tk.Button(self, text="Seleccionar…", command=self.select_c).grid(row=0, column=2, **pad)

        # Linker
        tk.Label(self, text="Linker script (linker.ld) [opcional]:").grid(row=1, column=0, sticky="e", **pad)
        tk.Entry(self, textvariable=self.path_linker, width=72).grid(row=1, column=1, **pad)
        tk.Button(self, text="Seleccionar…", command=self.select_linker).grid(row=1, column=2, **pad)

        # Toolchain y opciones
        tool_row = 2
        tk.Label(self, text="Toolchain prefix:").grid(row=tool_row, column=0, sticky="e", **pad)
        tk.Entry(self, textvariable=self.tool_prefix, width=20).grid(row=tool_row, column=1, sticky="w", **pad)

        wrap = tk.Frame(self)
        wrap.grid(row=tool_row, column=1, sticky="e", padx=8, pady=6)
        tk.Label(wrap, text="-march").pack(side="left", padx=(0,6))
        tk.Entry(wrap, textvariable=self.march, width=10).pack(side="left", padx=(0,18))
        tk.Label(wrap, text="-mabi").pack(side="left", padx=(0,6))
        tk.Entry(wrap, textvariable=self.mabi, width=10).pack(side="left")

        tk.Label(self, text="Dirección .text si no hay linker (hex):").grid(row=3, column=0, sticky="e", **pad)
        tk.Entry(self, textvariable=self.addr_text, width=20).grid(row=3, column=1, sticky="w", **pad)

        # Checkboxes salidas
        box = tk.Frame(self)
        box.grid(row=4, column=0, columnspan=3, sticky="w", **pad)
        tk.Checkbutton(box, text="Generar .s", variable=self.want_s).pack(side="left", padx=8)
        tk.Checkbutton(box, text="Generar .elf", variable=self.want_elf).pack(side="left", padx=8)
        tk.Checkbutton(box, text="Generar .hex", variable=self.want_hex).pack(side="left", padx=8)
        tk.Checkbutton(box, text="Generar .bin", variable=self.want_bin).pack(side="left", padx=8)

        # Botones acciones
        actions = tk.Frame(self)
        actions.grid(row=5, column=0, columnspan=3, sticky="w", **pad)
        tk.Button(actions, text="Analizar código", command=self.on_analizar).pack(side="left", padx=6)
        tk.Button(actions, text="Compilar / Generar", command=self.on_build).pack(side="left", padx=6)
        tk.Button(actions, text="Ejecutar en QEMU (.elf)", command=self.on_qemu).pack(side="left", padx=6)
        # >>> Nuevo botón: Limpiar consola <<<
        tk.Button(actions, text="Limpiar consola", command=self.on_clear_log).pack(side="left", padx=6)

        # Log
        self.log = ScrolledText(self, height=22)
        self.log.grid(row=6, column=0, columnspan=3, sticky="nsew", padx=8, pady=(4,10))
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._log("Listo. Selecciona un archivo .c para comenzar.\n")
        self._log("Sugerencia: usa Ctrl+L para limpiar la consola.\n")

    # ==== Handlers ====
    def select_c(self):
        f = filedialog.askopenfilename(filetypes=[("C source", "*.c")])
        if f:
            self.path_c.set(f)

    def select_linker(self):
        f = filedialog.askopenfilename(filetypes=[("Linker scripts", "*.ld *.lds"), ("Todos", "*.*")])
        if f:
            self.path_linker.set(f)

    def open_folder(self):
        if not self.path_c.get():
            return
        folder = os.path.dirname(self.path_c.get())
        if sys.platform.startswith("win"):
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    def on_analizar(self):
        path = self.path_c.get()
        if not path:
            messagebox.showwarning("Falta archivo", "Selecciona un archivo .c")
            return
        errs = analizar_codigo(path)
        if errs:
            self._log("⚠️ Errores encontrados:\n" + "\n".join(errs) + "\n")
        else:
            self._log("✅ El código parece compatible con TEC-RISC-V.\n")
            self._log("🔎 Nota: la arquitectura no permite accesos desalineados; revise estructuras/casts.\n")

    def on_build(self):
        if not self.path_c.get():
            messagebox.showwarning("Falta archivo", "Selecciona un archivo .c")
            return

        gcc = f"{self.tool_prefix.get()}gcc"
        objcopy = f"{self.tool_prefix.get()}objcopy"

        missing = [exe for exe in (gcc, objcopy) if not exists_in_path(exe)]
        if missing:
            self._log(f"❌ No se encontraron herramientas: {', '.join(missing)}\n"
                      f"Asegúrate de agregarlas al PATH.\n")
            return

        src = self.path_c.get()
        base = base_sin_ext(src)
        march = self.march.get().strip()
        mabi = self.mabi.get().strip()
        linker = self.path_linker.get().strip()
        addr_text = self.addr_text.get().strip()

        # 1) .s
        if self.want_s.get():
            cmd = [gcc, f"-march={march}", f"-mabi={mabi}", "-S", src, "-o", f"{base}.s"]
            self._run_and_log("Generando ensamblador (.s)", cmd)

        # 2) .elf
        if self.want_elf.get():
            if linker:
                cmd = [
                    gcc, f"-march={march}", f"-mabi={mabi}",
                    "-nostdlib", "-ffreestanding", "-fno-builtin",
                    "-T", linker,
                    "-o", f"{base}.elf",
                    f"{base}.s" if os.path.exists(f"{base}.s") else src
                ]
            else:
                self._log("ℹ️ No se seleccionó linker.ld.\n"
                          "   Recomendado: usar un linker con ENTRY(_start) y un startup.s para un arranque limpio.\n"
                          "   Continuando con fallback: -Wl,-Ttext para ubicar .text en la dirección indicada.\n")
                cmd = [
                    gcc, f"-march={march}", f"-mabi={mabi}",
                    "-nostdlib", "-ffreestanding", "-fno-builtin",
                    f"-Wl,-Ttext={addr_text}",
                    "-o", f"{base}.elf",
                    f"{base}.s" if os.path.exists(f"{base}.s") else src
                ]
            self._run_and_log("Compilando a ELF (.elf)", cmd)

        # 3) .hex
        if self.want_hex.get():
            if not os.path.exists(f"{base}.elf"):
                self._log("❌ No existe ELF. Genera primero .elf.\n")
            else:
                cmd = [objcopy, "-O", "ihex", f"{base}.elf", f"{base}.hex"]
                self._run_and_log("Generando HEX (.hex)", cmd)

        # 4) .bin
        if self.want_bin.get():
            if not os.path.exists(f"{base}.elf"):
                self._log("❌ No existe ELF. Genera primero .elf.\n")
            else:
                cmd = [objcopy, "-O", "binary", f"{base}.elf", f"{base}.bin"]
                self._run_and_log("Generando BIN (.bin)", cmd)

    def on_qemu(self):
        if not self.path_c.get():
            messagebox.showwarning("Falta archivo", "Selecciona un archivo .c y genera el .elf")
            return

        qemu = "qemu-system-riscv32"
        if not exists_in_path(qemu):
            self._log("❌ qemu-system-riscv32 no está en el PATH. Instálalo para usar esta opción.\n")
            return

        base = base_sin_ext(self.path_c.get())
        elf = f"{base}.elf"
        if not os.path.exists(elf):
            self._log("❌ No existe ELF. Genera primero .elf.\n")
            return

        cmd = [
            qemu,
            "-machine", "sifive_e",
            "-bios", "none",
            "-kernel", elf,
            "-nographic",
            "-serial", "mon:stdio"
        ]
        self._log("🚀 Ejecutando en QEMU (Ctrl+A luego X para salir)…\n")
        if sys.platform.startswith("win"):
            subprocess.Popen(["cmd", "/c"] + cmd)
        else:
            subprocess.Popen(cmd)

    # >>> Nuevo handler: limpiar el área de log <<<
    def on_clear_log(self):
        """Limpia por completo el contenido de la consola (área de log)."""
        self.log.delete("1.0", tk.END)
        # Mensaje breve para confirmar acción
        self._log("🧹 Consola limpiada. (Atajo: Ctrl+L)\n")

    def _run_and_log(self, title: str, cmd: list[str]):
        self._log(f"▶ {title}\n$ {' '.join(cmd)}\n")
        rc, out = run_cmd(cmd)
        self._log(out + ("\n" if not out.endswith("\n") else ""))
        if rc == 0:
            self._log("✅ OK\n\n")
        else:
            self._log(f"❌ Error (returncode={rc})\n\n")

    def _log(self, text: str):
        self.log.insert(tk.END, text)
        self.log.see(tk.END)

if __name__ == "__main__":
    app = App()
    app.mainloop()
