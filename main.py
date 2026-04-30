"""Точка входа в приложение учёта показаний счётчиков."""

from pathlib import Path
import tkinter as tk

from file_io import read_readings
from gui import CounterApp
from error_handler import ErrorHandler


def main() -> None:
  """Инициализирует данные и запускает GUI."""
  
  # Создаем инстанс синглтона при старте программы
  handler = ErrorHandler()
  handler.print_info("Запуск приложения...")
  
  filepath = Path("readings.txt")
  readings = read_readings(filepath)

  root = tk.Tk()
  app = CounterApp(root, readings, filepath)
  
  handler.print_info("Графический интерфейс запущен.")
  root.mainloop()


if __name__ == "__main__":
  main()