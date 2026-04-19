"""Модуль с графическим интерфейсом приложения."""

import tkinter as tk
import tkinter.scrolledtext as st
from datetime import date
from pathlib import Path
from tkinter import messagebox
from tkinter import ttk
from typing import List
import base64
import urllib.request
import webbrowser

from file_io import save_readings, read_readings
from models import CounterReading
from error_handler import ErrorHandler


class CounterApp:
  """Приложение для управления показаниями счётчиков."""

  def __init__(
      self, 
      root: tk.Tk, 
      initial_readings: List[CounterReading], 
      filepath: Path
  ):
    self.root = root
    self.root.title("Показания счётчиков")
    self.root.geometry("780x520")
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
        btn_frame, text="Добавить", command=self.add_reading
    ).pack(side="left", padx=5)
    tk.Button(
        btn_frame, text="Удалить выбранное", command=self.delete_selected
    ).pack(side="left", padx=5)
    tk.Button(
        btn_frame, text="Обновить таблицу", command=self.reload_from_file
    ).pack(side="left", padx=5)
    tk.Button(
        btn_frame, 
        text="[≡] Справка", 
        command=self._show_help,
        bg="#f0f0f0"
    ).pack(side="right", padx=5)

    self.root.columnconfigure(0, weight=1)
    self.root.rowconfigure(0, weight=1)

  def _refresh_table(self) -> None:
    for item in self.tree.get_children():
      self.tree.delete(item)

    sorted_list = sorted(self.readings, key=lambda x: (x.date, x.resource_type))
    for r in sorted_list:
      self.tree.insert(
          "",
          "end",
          values=(r.resource_type, f"{r.date:%d.%m.%Y}", f"{r.value:,.2f}"),
      )

  def add_reading(self) -> None:
    win = tk.Toplevel(self.root)
    win.title("Добавить показание")
    win.geometry("450x440")
    win.transient(self.root)
    win.grab_set()

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

    # --- ИНТЕРФЕЙС ЛОГОВ ---
    tk.Label(win, text="Журнал событий / Ошибки:", fg="grey").grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 0))
    log_area = st.ScrolledText(win, height=10, width=50, state="disabled", bg="#f4f4f4")
    log_area.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

    def log_callback(level: str, message: str) -> None:
        """Слот (Подписчик) для получения сообщений."""
        log_area.config(state="normal")
        log_area.insert(tk.END, f"[{level}] {message}\n")
        log_area.see(tk.END)
        log_area.config(state="disabled")

    # Подписка на Singleton
    handler = ErrorHandler()
    handler.subscribe(log_callback)
    handler.print_info("Готово к добавлению. Журнал активен.")

    def on_window_close():
        """Обязательная отписка при закрытии."""
        handler.unsubscribe(log_callback)
        win.destroy()
    
    win.protocol("WM_DELETE_WINDOW", on_window_close)
    # --- КОНЕЦ ИНТЕРФЕЙСА ЛОГОВ ---

    def save():
      try:
        res_type = e_type.get().strip()
        if not res_type:
          raise ValueError("Тип ресурса не может быть пустым")

        dt_str = e_date.get().strip()
        val_str = e_val.get().strip().replace(",", ".")

        reading = CounterReading(
            res_type, date.fromisoformat(dt_str), float(val_str)
        )
        self.readings.append(reading)
        
        handler.print_info(f"Добавлена запись: {res_type} = {val_str}")
        
        # Сохранение в файл. Все логи из file_io.py прилетят сюда же!
        save_readings(self.filepath, self.readings)
        
        self._refresh_table()
        
        # Очистка для следующего ввода
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
      # Если нужно, чтобы удаление тоже логировалось, можно перенести эту 
      # логику в отдельное окно или подписать главное окно на ErrorHandler.
      save_readings(self.filepath, self.readings)
      self._refresh_table()

  def _show_help(self) -> None:
    help_win = tk.Toplevel(self.root)
    help_win.title("Справочный центр")
    help_win.geometry("450x600")
    help_win.configure(bg="#ffffff") 
    help_win.transient(self.root)
    help_win.grab_set()
    
    icon_1 = "https://img.icons8.com/color/96/book.png"
    icon_2 = "https://img.icons8.com/color/96/opened-folder.png"
    
    body = tk.Frame(help_win, bg="white", padx=30, pady=20)
    body.pack(fill="both", expand=True)

    def get_img(url):
      try:
        with urllib.request.urlopen(url, timeout=5) as r:
          return tk.PhotoImage(data=base64.b64encode(r.read()))
      except Exception:
        return None

    self._img_doc = get_img(icon_1)
    self._img_fold = get_img(icon_2)

    tk.Label(
        body, text="Документация", font=("Arial", 18, "bold"), bg="white"
    ).pack(pady=10)

    if self._img_doc:
      img_1 = tk.Label(body, image=self._img_doc, bg="white", cursor="hand2")
      img_1.pack(pady=5)
      img_1.bind("<Button-1>", lambda e: webbrowser.open(icon_1))

    tk.Label(
        body, text="Читать мануал (откроется сайт)", fg="blue", bg="white"
    ).pack()

    tk.Frame(body, height=1, width=300, bg="#eeeeee").pack(pady=20)

    if self._img_fold:
      img_2 = tk.Label(body, image=self._img_fold, bg="white", cursor="hand2")
      img_2.pack(pady=5)
      img_2.bind("<Button-1>", lambda e: webbrowser.open(icon_2))

    tk.Label(
        body, text="Открыть файлы (в браузере)", fg="blue", bg="white"
    ).pack()

    tk.Button(
        body, text="ЗАКРЫТЬ СТРАНИЦУ", command=help_win.destroy,
        bg="#333333", fg="white", relief="flat", padx=20
    ).pack(side="bottom", pady=20)


  def reload_from_file(self) -> None:
    """Принудительно перечитывает данные из файла на диске."""
    handler = ErrorHandler()
    handler.print_info("Запрос на обновление: перечитываем файл с диска...")
    
    # Читаем свежий файл и перезаписываем список в памяти
    self.readings = read_readings(self.filepath)
    
    # Перерисовываем таблицу с новыми данными
    self._refresh_table()