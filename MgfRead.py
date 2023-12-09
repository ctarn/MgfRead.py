import ctypes
import os
import platform
import sys
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, scrolledtext

if platform.system() == "Windows":
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

win = tk.Tk()
win.title("MgfRead")
win.resizable(False, False)
main = ttk.Frame(win)
main.grid(column=0, row=0, padx=16, pady=8)

var_data = tk.StringVar()
var_out = tk.StringVar()

class Console:
    widget = None

    def __init__(self, widget):
        self.widget = widget

    def write(self, msg):
        self.widget.config(state="normal")
        self.widget.insert("end", msg)
        self.widget.config(state="disabled")
        self.widget.update()
        self.widget.see("end")

    def flush(self):
        pass

def select_data():
    filetypes = (("MSConvert MGF", "*.mgf"), ("All", "*.*"))
    files = filedialog.askopenfilenames(filetypes=filetypes)
    if len(files) > 1:
        print("multiple data selected:")
        [print(file) for file in files]
    var_data.set(";".join(files))
    if len(var_data.get()) > 0 and len(var_out.get()) == 0:
        var_out.set(os.path.join(os.path.dirname(files[0]), "out"))

def select_out():
    var_out.set(filedialog.askdirectory())

def parse_title(path_in, path_out):
    print("reading", path_in)
    os.makedirs(path_out, exist_ok=True)
    path = os.path.join(path_out, os.path.basename(path_in))
    print("writing", path)
    out = open(path, "w")
    lines = []
    write = True
    for line in open(path_in).readlines():
        if not line.startswith("TITLE"):
            lines.append(line)
        else:
            items = [item.strip() for item in line[6:].split(",")]
            charge = items[0].split(" File:\"")[0].split(".")[-1]
            fname = items[0].split(" File:\"")[1][:-3]
            scan_start = items[1][10:-1].split()[2].split("=")[1]
            scan_end = items[1][10:-1].split()[3].split("=")[1]
            lines.append(f"TITLE={fname}.{scan_start}.{scan_end}.{charge}.{0}.dta\n")
            write = len(charge) > 0
        if line.startswith("END IONS"):
            if write:
                out.writelines(lines)
            lines.clear()
            write = True
    out.close()

def run():
    btn_run.config(state="disabled")
    for data in var_data.get().split(";"):
        parse_title(data, var_out.get())
    btn_run.config(state="normal")

row=0
ttk.Label(main, text="Data:").grid(column=0, row=row, sticky="W")
ttk.Entry(main, textvariable=var_data, width=64).grid(column=1, row=row, sticky="WE")
ttk.Button(main, text="Select", command=select_data).grid(column=2, row=row, sticky="W")

row += 1
ttk.Label(main, text="Save to:").grid(column=0, row=row, sticky="W")
ttk.Entry(main, textvariable=var_out, width=64).grid(column=1, row=row, sticky="WE")
ttk.Button(main, text="Select", command=select_out).grid(column=2, row=row, sticky="W")

row += 1
btn_run = ttk.Button(main, text="RUN", command=lambda: threading.Thread(target=run).start())
btn_run.grid(column=0, row=row, columnspan=3)

row += 1
console = scrolledtext.ScrolledText(main, height=16)
console.config(state="disabled")
console.grid(column=0, row=row, columnspan=3, sticky="WE")

row += 1
ttk.Label(main, text="MgfRead v0.0.0\nCopyright © 2023 Tarn Yeong Ching\nhttp://ctarn.io", justify="center").grid(column=0, row=row, columnspan=3)

sys.stdout = Console(console)
sys.stderr = Console(console)

main.mainloop()
