"""Функции для работы с файловой системой."""

import logging
from pathlib import Path
from typing import List

from models import CounterReading
from models import parse_reading_parts


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
  readings: List[CounterReading] = []

  if not path.is_file():
    return readings

  with path.open(encoding="utf-8") as f:
    for i, line in enumerate(f, start=1):
      try:
        readings.append(parse_line(line))
      except ValueError as e:
        logging.warning("Строка %d: %s → пропущена", i, e)

  return readings


def save_readings(path: Path, readings: List[CounterReading]) -> None:
  """Сохраняет список показаний в файл."""
  with path.open("w", encoding="utf-8") as f:
    for r in readings:
      f.write(f'"{r.resource_type}" {r.date:%Y.%m.%d} {r.value:.2f}\n')