"""Функции для работы с файловой системой."""

from pathlib import Path
from typing import List

from models import CounterReading, parse_reading_parts
from error_handler import ErrorHandler


def parse_line(line: str) -> CounterReading:
  """Парсит одну строку файла в объект CounterReading."""
  line = line.strip()
  if not line or line.startswith("#"):
    raise ValueError("Пустая строка или комментарий")

  parts = line.split('"', 2)
  if len(parts) < 3:
    raise ValueError("Ожидается название ресурса в кавычках")

  resource_type = parts[1].strip()
  tail = parts[2].strip().split()

  if len(tail) < 2:
    raise ValueError("Не найдены дата и/или значение")

  date_str, value_str = tail[0], " ".join(tail[1:])
  return parse_reading_parts(resource_type, date_str, value_str)


def read_readings(path: Path) -> List[CounterReading]:
  """Читает все валидные показания из файла."""
  readings: List[CounterReading] =[]
  handler = ErrorHandler()

  if not path.is_file():
    handler.print_warning(f"Файл для чтения не найден: {path}")
    return readings

  handler.print_info(f"Открытие файла для чтения: {path}")
  with path.open(encoding="utf-8") as f:
    for i, line in enumerate(f, start=1):
      try:
        readings.append(parse_line(line))
      except ValueError as e:
        handler.print_warning(f"Строка {i}: {e} → пропущена")
        
  handler.print_info(f"Успешно прочитано записей: {len(readings)}")
  return readings


def save_readings(path: Path, readings: List[CounterReading]) -> None:
  """Сохраняет список показаний в файл."""
  handler = ErrorHandler()
  handler.print_info(f"Обновление файла: {path}")
  try:
    with path.open("w", encoding="utf-8") as f:
      for r in readings:
        f.write(f'"{r.resource_type}" {r.date:%Y.%m.%d} {r.value:.2f}\n')
    handler.print_info("Файл успешно сохранен.")
  except Exception as e:
    handler.print_error(f"Ошибка при сохранении файла: {e}")