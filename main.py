"""Точка входа в приложение учёта показаний счётчиков."""

import logging
from pathlib import Path
import tkinter as tk

from file_io import read_readings
from gui import CounterApp


def main() -> None:
  """Инициализирует данные и запускает GUI."""
  logging.basicConfig(level=logging.INFO)
  filepath = Path("readings.txt")
  readings = read_readings(filepath)

  root = tk.Tk()
  app = CounterApp(root, readings, filepath)
  root.mainloop()


if __name__ == "__main__":
  main()