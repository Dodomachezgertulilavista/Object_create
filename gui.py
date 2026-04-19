"""Модуль с графическим интерфейсом приложения."""

import tkinter as tk
import tkinter.scrolledtext as st
import tkinter.filedialog as fd
import webbrowser
from datetime import date
from pathlib import Path
from tkinter import messagebox
from tkinter import ttk
from typing import List

from file_io import save_readings, read_readings
from models import CounterReading
from error_handler import ErrorHandler
from command_processor import execute_commands


class CounterApp:
  def __init__(
      self, 
      root: tk.Tk, 
      initial_readings: List[CounterReading], 
      filepath: Path
  ):
    self.root = root
    self.root.title("Показания счётчиков")
    self.root.geometry("820x520")
    self.root.resizable = [False, False]

    self.readings = initial_readings.copy()
    self.filepath = filepath

    self._create_widgets()
    self._refresh_table()

  def _create_widgets(self) -> None:
    columns = ("resource", "date", "value")
    self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)

    self.tree.heading("resource", text="Тип ресурса")
    self.tree.heading("date", text="Дата")
    self.tree.heading("value", text="Значение")

    self.tree.column("resource", width=220, anchor="w")
    self.tree.column("date", width=140, anchor="center")
    self.tree.column("value", width=140, anchor="e")

    self.tree.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    btn_frame = tk.Frame(self.root)
    btn_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

    tk.Button(
        btn_frame, text="Добавить/Журнал", command=self.add_reading
    ).pack(side="left", padx=5)
    
    tk.Button(
        btn_frame, text="Удалить выбранное", command=self.delete_selected
    ).pack(side="left", padx=5)
    
    tk.Button(
        btn_frame, text="Обновить таблицу", command=self.reload_from_file
    ).pack(side="left", padx=5)

    tk.Button(
        btn_frame, text="Выполнить скрипт", command=self.run_script, bg="#e0ffe0"
    ).pack(side="left", padx=5)

    tk.Button(
        btn_frame, text="[≡] Справка", command=self._show_help, bg="#f0f0f0"
    ).pack(side="right", padx=5)

    self.root.columnconfigure(0, weight=1)
    self.root.rowconfigure(0, weight=1)

  def _refresh_table(self) -> None:
    for item in self.tree.get_children():
      self.tree.delete(item)

    sorted_list = sorted(self.readings, key=lambda x: (x.date, x.resource_type))
    for r in sorted_list:
      self.tree.insert("", "end", values=(r.resource_type, f"{r.date:%d.%m.%Y}", f"{r.value:,.2f}"))

  def reload_from_file(self) -> None:
    handler = ErrorHandler()
    handler.print_info("Запрос на обновление: перечитываем файл с диска...")
    self.readings = read_readings(self.filepath)
    self._refresh_table()

  def run_script(self) -> None:
    script_path = fd.askopenfilename(
        title="Выберите файл скрипта",
        filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
    )
    if not script_path:
        return
        
    execute_commands(Path(script_path), self.readings)
    save_readings(self.filepath, self.readings)
    self._refresh_table()

  def add_reading(self) -> None:
    win = tk.Toplevel(self.root)
    win.title("Добавить показание / Журнал")
    win.geometry("450x440")
    win.transient(self.root)

    tk.Label(win, text="Тип ресурса:").grid(row=0, column=0, padx=10, pady=8, sticky="e")
    e_type = tk.Entry(win, width=30)
    e_type.grid(row=0, column=1, pady=8)

    tk.Label(win, text="Дата (гггг-мм-дд):").grid(row=1, column=0, padx=10, pady=8, sticky="e")
    e_date = tk.Entry(win, width=30)
    e_date.grid(row=1, column=1, pady=8)
    e_date.insert(0, date.today().isoformat())

    tk.Label(win, text="Значение:").grid(row=2, column=0, padx=10, pady=8, sticky="e")
    e_val = tk.Entry(win, width=30)
    e_val.grid(row=2, column=1, pady=8)

    tk.Label(win, text="Журнал событий / Ошибки:", fg="grey").grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 0))
    log_area = st.ScrolledText(win, height=10, width=50, state="disabled", bg="#f4f4f4")
    log_area.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

    def log_callback(level: str, message: str) -> None:
        log_area.config(state="normal")
        log_area.insert(tk.END, f"[{level}] {message}\n")
        log_area.see(tk.END)
        log_area.config(state="disabled")

    handler = ErrorHandler()
    handler.subscribe(log_callback)
    
    def on_window_close():
        handler.unsubscribe(log_callback)
        win.destroy()
    
    win.protocol("WM_DELETE_WINDOW", on_window_close)

    def save():
      try:
        res_type = e_type.get().strip()
        if not res_type:
          raise ValueError("Тип ресурса не может быть пустым")

        dt_str = e_date.get().strip()
        val_str = e_val.get().strip().replace(",", ".")

        reading = CounterReading(res_type, date.fromisoformat(dt_str), float(val_str))
        self.readings.append(reading)
        
        handler.print_info(f"Добавлена запись: {res_type} = {val_str}")
        save_readings(self.filepath, self.readings)
        self._refresh_table()
        
        e_val.delete(0, tk.END)
        e_type.delete(0, tk.END)
        
      except ValueError as e:
        handler.print_error(f"Некорректный ввод: {e}")

    tk.Button(win, text="Сохранить", command=save).grid(row=3, column=1, pady=10, sticky="e")
    tk.Button(win, text="Закрыть", command=on_window_close).grid(row=3, column=0, pady=10, sticky="w", padx=10)

  def delete_selected(self) -> None:
    selected = self.tree.selection()
    if not selected:
      messagebox.showwarning("Нет выбора", "Выделите строку для удаления")
      return

    if not messagebox.askyesno("Подтверждение", "Удалить выбранное показание?"):
      return

    values = self.tree.item(selected[0])["values"]
    to_remove = None
    for r in self.readings:
      if (r.resource_type == values[0] and 
          f"{r.date:%d.%m.%Y}" == values[1] and 
          f"{r.value:,.2f}" == values[2]):
        to_remove = r
        break

    if to_remove:
      self.readings.remove(to_remove)
      save_readings(self.filepath, self.readings)
      self._refresh_table()

  # --- НОВАЯ ВЕРСИЯ С НАСТОЯЩИМ HTML ---
  def _show_help(self) -> None:
    """Читает внешний файл help.html и отображает его прямо в окне Tkinter."""
    handler = ErrorHandler()
    help_path = Path("help.html")
    
    help_win = tk.Toplevel(self.root)
    help_win.title("Справочный центр")
    help_win.geometry("550x550")
    help_win.transient(self.root)

    # 1. Проверяем, существует ли файл
    if not help_path.is_file():
        handler.print_error("Файл help.html не найден в папке проекта!")
        messagebox.showerror("Ошибка", "Файл help.html не найден!")
        help_win.destroy()
        return

    # 2. Читаем готовый файл
    try:
        with help_path.open("r", encoding="utf-8") as f:
            html_content = f.read()
            handler.print_info("Файл help.html успешно прочитан.")
    except Exception as e:
        handler.print_error(f"Ошибка чтения help.html: {e}")
        return

    # 3. Пытаемся отобразить HTML внутри Tkinter
    try:
        # Пытаемся импортировать библиотеку для рендера HTML
        from tkhtmlview import HTMLLabel
        
        html_label = HTMLLabel(help_win, html=html_content)
        html_label.pack(fill="both", expand=True, padx=10, pady=10)
        handler.print_info("Справка отображена в режиме HTML.")
        
    except ImportError:
        # ЗАЩИТА: Если библиотека tkhtmlview НЕ установлена, 
        # показываем текст, очистив его от тегов!
        handler.print_warning("Библиотека tkhtmlview не установлена. Использую текстовый режим.")
        
        import re # Импортируем регулярные выражения для очистки тегов
        
        text_area = st.ScrolledText(help_win, wrap=tk.WORD, font=("Arial", 11))
        text_area.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Удаляем секцию <head> и её содержимое
        clean_text = re.sub(r'<head.*?>.*?</head>', '', html_content, flags=re.DOTALL|re.IGNORECASE)
        # Заменяем некоторые теги на переносы строк для красоты
        clean_text = re.sub(r'<br/?>|</p>|</h1>|</h2>|</ul>', '\n\n', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'<li>', ' • ', clean_text, flags=re.IGNORECASE)
        # Удаляем все оставшиеся теги
        clean_text = re.sub(r'<[^>]+>', '', clean_text)
        
        text_area.insert(tk.END, "--- РЕЖИМ БЕЗ ФОРМАТИРОВАНИЯ ---\n")
        text_area.insert(tk.END, "(Для красивого отображения установите: pip install tkhtmlview)\n\n")
        text_area.insert(tk.END, clean_text.strip())
        text_area.config(state="disabled")

    tk.Button(help_win, text="Закрыть", command=help_win.destroy).pack(pady=10)