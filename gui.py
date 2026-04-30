import tkinter as tk
from tkinter import ttk, scrolledtext as st, filedialog as fd, messagebox
import re
from pathlib import Path
from models import CounterReading, parse_reading_parts
from file_io import save_readings, read_readings
from error_handler import ErrorHandler
from command_processor import execute_commands

class CounterApp:
    def __init__(self, root, initial_readings, filepath):
        self.root = root
        self.root.title("Учёт ресурсов (Lab4)")
        self.root.geometry("900x500")
        self.readings = initial_readings
        self.filepath = filepath
        self._create_widgets()

    def _create_widgets(self):
        cols = ("res", "date", "val", "qual")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings")
        self.tree.heading("res", text="Ресурс"); self.tree.heading("date", text="Дата")
        self.tree.heading("val", text="Значение"); self.tree.heading("qual", text="Качество")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        f = tk.Frame(self.root)
        f.pack(fill="x", padx=10, pady=5)
        tk.Button(f, text="Журнал / Добавить", command=self.add_reading).pack(side="left", padx=2)
        tk.Button(f, text="Обновить", command=self.refresh).pack(side="left", padx=2)
        tk.Button(f, text="Скрипт", command=self.run_script).pack(side="left", padx=2)
        tk.Button(f, text="Справка", command=self.show_help).pack(side="right", padx=2)

    def refresh(self):
        self.readings = read_readings(self.filepath)
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in self.readings:
            self.tree.insert("", "end", values=(r.resource_type, r.date, r.value, r.quality))

    def run_script(self):
        p = fd.askopenfilename()
        if p:
            execute_commands(Path(p), self.readings)
            save_readings(self.filepath, self.readings)
            self.refresh()

    def add_reading(self):
        win = tk.Toplevel(self.root)
        win.geometry("450x450")
        
        # Поля ввода
        inputs = []
        for i, lbl in enumerate(["Тип", "Дата (ГГГГ-ММ-ДД)", "Значение", "Качество"]):
            tk.Label(win, text=lbl).grid(row=i, column=0)
            e = tk.Entry(win); e.grid(row=i, column=1); inputs.append(e)
        
        log = st.ScrolledText(win, height=10, state="disabled")
        log.grid(row=5, column=0, columnspan=2)

        def cb(lvl, msg):
            log.config(state="normal"); log.insert("end", f"[{lvl}] {msg}\n"); log.see("end"); log.config(state="disabled")

        h = ErrorHandler(); h.subscribe(cb)
        win.protocol("WM_DELETE_WINDOW", lambda: [h.unsubscribe(cb), win.destroy()])

        def save():
            try:
                r = parse_reading_parts(inputs[0].get(), inputs[1].get(), inputs[2].get(), inputs[3].get())
                self.readings.append(r); save_readings(self.filepath, self.readings); h.print_info("ОК"); self.refresh()
            except Exception as e: h.print_error(str(e))
        
        tk.Button(win, text="Сохранить", command=save).grid(row=4, column=1)

    def show_help(self):
        h_win = tk.Toplevel(self.root); h_win.geometry("500x500")
        p = Path("help.html")
        if not p.exists(): return
        content = p.read_text(encoding="utf-8")
        try:
            from tkhtmlview import HTMLLabel
            # Очистка от CSS, который вешает tkhtmlview
            clean = re.sub(r'<(style|head|title).*?>.*?</\1>', '', content, flags=re.S|re.I)
            HTMLLabel(h_win, html=clean).pack(fill="both", expand=True)
        except:
            t = st.ScrolledText(h_win); t.pack(); t.insert("1.0", re.sub('<[^>]*>', '', content))
