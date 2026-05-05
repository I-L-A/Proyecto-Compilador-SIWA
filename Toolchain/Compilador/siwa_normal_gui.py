
"""
Requisitos (Ubuntu/Debian):
  sudo apt update
  sudo apt install gcc-riscv64-linux-gnu binutils-riscv64-linux-gnu qemu-user qemu-user-binfmt

Uso:
  python3 siwa_builder_gui.py
"""

import os
import subprocess
import threading
import shlex
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinter.scrolledtext import ScrolledText

# --------- Utilidad ---------
def which(cmd):
    from shutil import which as _which
    return _which(cmd)

def quote(s: str) -> str:
    return shlex.quote(str(s))

def run_cmd(cmd, cwd=None):
    """Ejecuta comando y retorna (returncode, stdout, stderr)."""
    try:
        p = subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return p.returncode, p.stdout, p.stderr
    except FileNotFoundError as e:
        return 127, "", str(e)

def append_console(text_widget: ScrolledText, msg: str):
    text_widget.configure(state="normal")
    text_widget.insert("end", msg + "\n")
    text_widget.see("end")
    text_widget.configure(state="disabled")

# --------- Lógica de construcción ---------
class BuilderConfig:
    def __init__(self):
        # Arquitectura por defecto: rv64 (Linux user-mode)
        self.arch = "rv64"  # "rv64" o "rv32"
        self.tool_cc = "riscv64-linux-gnu-gcc"
        self.tool_objcopy = "riscv64-linux-gnu-objcopy"
        self.tool_objdump = "riscv64-linux-gnu-objdump"
        self.tool_qemu = "qemu-riscv64"
        self.opt_level = "-O2"
        self.static = True
        # Formato de .hex: intel (objcopy) o verilog32le (palabras 32-bit little-endian para $readmemh)
        self.hex_format = "intel"  # "intel" | "verilog32le"

class RiscvBuilder:
    def __init__(self, cfg: BuilderConfig, console: ScrolledText):
        self.cfg = cfg
        self.console = console

    def check_tools(self):
        missing = []
        for t in [self.cfg.tool_cc, self.cfg.tool_objcopy, self.cfg.tool_qemu]:
            if not which(t):
                missing.append(t)
        if missing:
            append_console(self.console, f"⚠️ Herramientas faltantes: {', '.join(missing)}")
            append_console(self.console, "Instala en Ubuntu/Debian:\n  sudo apt install gcc-riscv64-linux-gnu binutils-riscv64-linux-gnu qemu-user qemu-user-binfmt")
        return not missing

    def build(self, c_path: Path, out_s: bool, out_elf: bool, out_bin: bool, out_hex: bool):
        if not self.check_tools():
            messagebox.showerror("Faltan herramientas", "Instala las herramientas RISC‑V/QEMU antes de continuar.")
            return None

        if not c_path.exists():
            append_console(self.console, f"❌ No existe: {c_path}")
            return None

        # Directorio de salida = carpeta del .c
        out_dir = c_path.parent
        stem = c_path.stem

        # 1) .s (ensamblador)
        s_path = out_dir / f"{stem}.s"
        if out_s or out_elf or out_bin or out_hex:
            args_s = [self.cfg.tool_cc, self.cfg.opt_level, "-S", str(c_path), "-o", str(s_path)]
            append_console(self.console, "→ Generando .s:\n  " + " ".join(map(quote, args_s)))
            rc, so, se = run_cmd(args_s, cwd=out_dir)
            append_console(self.console, so.strip())
            if rc != 0:
                append_console(self.console, se.strip())
                messagebox.showerror("Error al compilar a .s", se)
                return None
            else:
                append_console(self.console, f"✅ Creado: {s_path}")

        # 2) .elf (ejecutable estático para user-mode QEMU)
        elf_path = out_dir / f"{stem}.elf"
        if out_elf or out_bin or out_hex:
            cc_flags = [self.cfg.opt_level]
            if self.cfg.static:
                cc_flags.append("-static")
            args_elf = [self.cfg.tool_cc] + cc_flags + [str(c_path), "-o", str(elf_path)]
            append_console(self.console, "→ Generando .elf:\n  " + " ".join(map(quote, args_elf)))
            rc, so, se = run_cmd(args_elf, cwd=out_dir)
            append_console(self.console, so.strip())
            if rc != 0:
                append_console(self.console, se.strip())
                messagebox.showerror("Error al compilar a .elf", se)
                return None
            else:
                size_rc, size_out, size_err = run_cmd(["/usr/bin/env", "bash", "-lc", f"stat -c %s {quote(elf_path)} || wc -c < {quote(elf_path)}"])
                if size_rc == 0 and size_out.strip().isdigit():
                    kb = int(size_out.strip()) / 1024.0
                    append_console(self.console, f"✅ Creado: {elf_path} ({kb:.1f} KiB)")
                else:
                    append_console(self.console, f"✅ Creado: {elf_path}")

        # 3) .bin
        bin_path = out_dir / f"{stem}.bin"
        if out_bin:
            args_bin = [self.cfg.tool_objcopy, "-O", "binary", str(elf_path), str(bin_path)]
            append_console(self.console, "→ Generando .bin:\n  " + " ".join(map(quote, args_bin)))
            rc, so, se = run_cmd(args_bin, cwd=out_dir)
            if rc != 0:
                append_console(self.console, se.strip())
                messagebox.showerror("Error al crear .bin", se)
                return None
            else:
                append_console(self.console, f"✅ Creado: {bin_path}")

        # 4) .hex (Intel HEX)
        hex_path = out_dir / f"{stem}.hex"
        if out_hex:
            if self.cfg.hex_format == "intel":
                # Intel HEX clásico desde ELF (secciones)
                args_hex = [self.cfg.tool_objcopy, "-O", "ihex", str(elf_path), str(hex_path)]
                append_console(self.console, "→ Generando .hex (Intel HEX):\n  " + " ".join(map(quote, args_hex)))
                rc, so, se = run_cmd(args_hex, cwd=out_dir)
                if rc != 0:
                    append_console(self.console, se.strip())
                    messagebox.showerror("Error al crear .hex", se)
                    return None
                else:
                    append_console(self.console, f"✅ Creado: {hex_path}")
            else:
                # Verilog 32-bit Little Endian ($readmemh) desde .bin
                # 1) asegurarnos de tener .bin
                bin_path_local = out_dir / f"{stem}.bin"
                if not out_bin:
                    args_bin = [self.cfg.tool_objcopy, "-O", "binary", str(elf_path), str(bin_path_local)]
                    append_console(self.console, "→ Generando .bin intermedio para .hex (verilog32le):\n  " + " ".join(map(quote, args_bin)))
                    rc, so, se = run_cmd(args_bin, cwd=out_dir)
                    if rc != 0:
                        append_console(self.console, se.strip())
                        messagebox.showerror("Error al crear .bin intermedio", se)
                        return None
                # 2) leer bin y volcar palabras LE de 32 bits
                data = (out_dir / f"{stem}.bin").read_bytes()
                # padding a múltiplo de 4
                if len(data) % 4 != 0:
                    data += b"\x00" * (4 - (len(data) % 4))
                lines = []
                for i in range(0, len(data), 4):
                    w = int.from_bytes(data[i:i+4], byteorder="little", signed=False)
                    lines.append(f"{w:08x}")
                (out_dir / f"{stem}.hex").write_text("\n".join(lines) + "\n", encoding="ascii")
                append_console(self.console, f"✅ Creado: {hex_path} (formato Verilog 32-bit LE, $readmemh)")

        return {
            "s": s_path if s_path.exists() else None,
            "elf": elf_path if elf_path.exists() else None,
            "bin": bin_path if bin_path.exists() else None,
            "hex": hex_path if hex_path.exists() else None,
        }

    def run_qemu_user(self, elf_path: Path):
        if not which(self.cfg.tool_qemu):
            messagebox.showerror("QEMU no encontrado", f"No se encontró {self.cfg.tool_qemu} en PATH.")
            return
        if not elf_path or not elf_path.exists():
            messagebox.showerror("ELF no encontrado", "Primero construye o selecciona un .elf válido.")
            return

        cmd = [self.cfg.tool_qemu, str(elf_path)]
        append_console(self.console, "▶ Ejecutando en QEMU (user-mode):\n  " + " ".join(map(quote, cmd)))
        # Ejecutar en hilo para no bloquear la GUI
        def _run():
            rc, so, se = run_cmd(cmd, cwd=elf_path.parent)
            # Mostrar salida
            if so:
                append_console(self.console, so.rstrip())
            if se:
                append_console(self.console, se.rstrip())
            append_console(self.console, f"■ QEMU terminó con código {rc}")
        threading.Thread(target=_run, daemon=True).start()

# --------- GUI ---------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SIWA Builder GUI — RISC‑V")
        self.geometry("860x600")
        self.minsize(800, 560)

        self.cfg = BuilderConfig()
        self.builder = None
        self.c_file: Path | None = None
        self.last_artifacts = {}

        self.create_widgets()

    def create_widgets(self):
        # Frame superior: selección de archivo
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Archivo .c:").grid(row=0, column=0, sticky="w")
        self.entry_c = ttk.Entry(top, width=80)
        self.entry_c.grid(row=0, column=1, padx=8, sticky="we")
        top.columnconfigure(1, weight=1)
        ttk.Button(top, text="Seleccionar…", command=self.select_c).grid(row=0, column=2)

        # Opciones de salida
        opts = ttk.Labelframe(self, text="Artefactos a generar", padding=10)
        opts.pack(fill="x", padx=10, pady=(0, 8))

        self.var_s = tk.BooleanVar(value=True)
        self.var_elf = tk.BooleanVar(value=True)
        self.var_bin = tk.BooleanVar(value=False)
        self.var_hex = tk.BooleanVar(value=False)

        ttk.Checkbutton(opts, text=".s (ensamblador)", variable=self.var_s).grid(row=0, column=0, sticky="w", padx=4)
        ttk.Checkbutton(opts, text=".elf (ejecutable estático)", variable=self.var_elf).grid(row=0, column=1, sticky="w", padx=4)
        ttk.Checkbutton(opts, text=".bin (raw)", variable=self.var_bin).grid(row=0, column=2, sticky="w", padx=4)
        ttk.Checkbutton(opts, text=".hex (RISCV HEX)", variable=self.var_hex).grid(row=0, column=3, sticky="w", padx=4)

        # Configuración de compilación
        cfgf = ttk.Labelframe(self, text="Configuración", padding=10)
        cfgf.pack(fill="x", padx=10, pady=(0, 8))

        ttk.Label(cfgf, text="Optimizacion:").grid(row=0, column=0, sticky="w")
        self.combo_opt = ttk.Combobox(cfgf, values=["-O0", "-O1", "-O2", "-O3", "-Os", "-Ofast"], state="readonly")
        self.combo_opt.set(self.cfg.opt_level)
        self.combo_opt.grid(row=0, column=1, sticky="w", padx=4)

        self.var_static = tk.BooleanVar(value=self.cfg.static)
        ttk.Checkbutton(cfgf, text="Link estático (-static)", variable=self.var_static).grid(row=0, column=2, sticky="w", padx=10)

        # Arquitectura
        ttk.Label(cfgf, text="Arquitectura:").grid(row=1, column=0, sticky="w", pady=(8,0))
        self.combo_arch = ttk.Combobox(cfgf, values=["rv64 (Linux user-mode)","rv32 (Linux user-mode)"], state="readonly", width=26)
        self.combo_arch.set("rv64 (Linux user-mode)")
        self.combo_arch.grid(row=1, column=1, sticky="w", padx=4, pady=(8,0))

        # Formato .hex
        ttk.Label(cfgf, text="Formato .hex:").grid(row=1, column=2, sticky="e", pady=(8,0))
        self.combo_hex = ttk.Combobox(cfgf, values=["intel (objcopy)", "verilog32le ($readmemh)"], state="readonly", width=26)
        self.combo_hex.set("intel (objcopy)")
        self.combo_hex.grid(row=1, column=3, sticky="w", padx=4, pady=(8,0))

        # Toolchain visibles (se actualizan con la arquitectura)
        ttk.Label(cfgf, text="Toolchain:").grid(row=2, column=0, sticky="w", pady=(8,0))
        ttk.Label(cfgf, text="Toolchain:").grid(row=1, column=0, sticky="w", pady=(8,0))
        self.entry_cc = ttk.Entry(cfgf, width=24)
        self.entry_cc.insert(0, self.cfg.tool_cc)
        self.entry_cc.grid(row=2, column=1, sticky="w", padx=4, pady=(8,0))

        ttk.Label(cfgf, text="objcopy:").grid(row=2, column=2, sticky="e", pady=(8,0))
        self.entry_objcopy = ttk.Entry(cfgf, width=24)
        self.entry_objcopy.insert(0, self.cfg.tool_objcopy)
        self.entry_objcopy.grid(row=2, column=3, sticky="w", padx=4, pady=(8,0))

        ttk.Label(cfgf, text="QEMU:").grid(row=2, column=4, sticky="e", pady=(8,0))
        self.entry_qemu = ttk.Entry(cfgf, width=24)
        self.entry_qemu.insert(0, self.cfg.tool_qemu)
        self.entry_qemu.grid(row=2, column=5, sticky="w", padx=4, pady=(8,0))

        # Botones de acción
        actions = ttk.Frame(self, padding=10)
        actions.pack(fill="x")

        self.btn_build = ttk.Button(actions, text="Construir", command=self.on_build)
        self.btn_build.pack(side="left")

        self.btn_run = ttk.Button(actions, text="▶ Ejecutar .elf en QEMU", command=self.on_run, state="disabled")
        self.btn_run.pack(side="left", padx=8)

        self.btn_clear = ttk.Button(actions, text="Limpiar consola", command=self.on_clear)
        self.btn_clear.pack(side="right")

        # Consola
        self.console = ScrolledText(self, height=18, state="disabled")
        self.console.pack(fill="both", expand=True, padx=10, pady=(0,10))

        # Creditos
        credits = ttk.Label(self, text="SIWA Builder GUI — RISC‑V | por Iván + ChatGPT", anchor="e")
        credits.pack(fill="x", padx=10, pady=(0,10))

        self.builder = RiscvBuilder(self.cfg, self.console)

        def _apply_arch_defaults(event=None):
            arch = "rv32" if self.combo_arch.get().startswith("rv32") else "rv64"
            if arch == "rv32":
                self.entry_cc.delete(0, "end"); self.entry_cc.insert(0, "riscv32-linux-gnu-gcc")
                self.entry_objcopy.delete(0, "end"); self.entry_objcopy.insert(0, "riscv32-linux-gnu-objcopy")
                self.entry_qemu.delete(0, "end"); self.entry_qemu.insert(0, "qemu-riscv32")
            else:
                self.entry_cc.delete(0, "end"); self.entry_cc.insert(0, "riscv64-linux-gnu-gcc")
                self.entry_objcopy.delete(0, "end"); self.entry_objcopy.insert(0, "riscv64-linux-gnu-objcopy")
                self.entry_qemu.delete(0, "end"); self.entry_qemu.insert(0, "qemu-riscv64")
        self.combo_arch.bind("<<ComboboxSelected>>", _apply_arch_defaults)

    def select_c(self):
        path = filedialog.askopenfilename(
            title="Selecciona archivo .c",
            filetypes=[("C source", "*.c"), ("Todos", "*.*")]
        )
        if path:
            self.c_file = Path(path)
            self.entry_c.delete(0, "end")
            self.entry_c.insert(0, str(self.c_file))
            self.btn_run.configure(state="disabled")

    def on_build(self):
        # Sin bloquear GUI
        def _work():
            try:
                self.cfg.opt_level = self.combo_opt.get().strip() or "-O2"
                self.cfg.static = bool(self.var_static.get())
                # Arquitectura
                arch_sel = self.combo_arch.get()
                self.cfg.arch = "rv32" if arch_sel.startswith("rv32") else "rv64"
                # Formato hex
                hex_sel = self.combo_hex.get()
                self.cfg.hex_format = "verilog32le" if hex_sel.startswith("verilog") else "intel"
                # Toolchain (se pueden sobreescribir manualmente por el usuario)
                if self.cfg.arch == "rv32":
                    default_cc = "riscv32-linux-gnu-gcc"
                    default_objcopy = "riscv32-linux-gnu-objcopy"
                    default_qemu = "qemu-riscv32"
                else:
                    default_cc = "riscv64-linux-gnu-gcc"
                    default_objcopy = "riscv64-linux-gnu-objcopy"
                    default_qemu = "qemu-riscv64"
                self.cfg.tool_cc = self.entry_cc.get().strip() or default_cc
                self.cfg.tool_objcopy = self.entry_objcopy.get().strip() or default_objcopy
                self.cfg.tool_qemu = self.entry_qemu.get().strip() or default_qemu

                c_path = Path(self.entry_c.get().strip())
                if not c_path or not c_path.exists():
                    messagebox.showwarning("Falta archivo", "Selecciona primero un archivo .c válido.")
                    return

                out_s = bool(self.var_s.get())
                out_elf = bool(self.var_elf.get())
                out_bin = bool(self.var_bin.get())
                out_hex = bool(self.var_hex.get())

                append_console(self.console, "================= BUILD =================")
                self.last_artifacts = self.builder.build(c_path, out_s, out_elf, out_bin, out_hex)

                # Habilitar botón run si hay ELF
                if self.last_artifacts and self.last_artifacts.get("elf"):
                    self.btn_run.configure(state="normal")
                else:
                    self.btn_run.configure(state="disabled")
            except Exception as e:
                messagebox.showerror("Error inesperado", str(e))

        threading.Thread(target=_work, daemon=True).start()

    def on_run(self):
        elf = None
        if self.last_artifacts:
            elf = self.last_artifacts.get("elf")
        if not elf:
            # Intentar deducir desde el .c
            c_path = Path(self.entry_c.get().strip())
            if c_path.exists():
                elf_try = c_path.with_suffix(".elf")
                if elf_try.exists():
                    elf = elf_try

        if not elf:
            messagebox.showwarning("Sin .elf", "No se encontró el .elf. Por favor, construye primero.")
            return

        self.builder.run_qemu_user(Path(elf))

    def on_clear(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

if __name__ == "__main__":
    App().mainloop()
