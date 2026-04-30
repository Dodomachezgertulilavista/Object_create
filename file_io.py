from pathlib import Path
from typing import List
from models import CounterReading, parse_reading_parts
from error_handler import ErrorHandler

def parse_line(line: str) -> CounterReading:
    line = line.strip()
    if not line or line.startswith("#"): raise ValueError("Пусто")
    parts = line.split('"', 2)
    if len(parts) < 3: raise ValueError("Формат: \"Тип\" Дата Значение Качество")
    
    res_type = parts[1]
    tail = parts[2].strip().split(maxsplit=2)
    if len(tail) < 3: raise ValueError("Недостаточно данных")
    
    return parse_reading_parts(res_type, tail[0], tail[1], tail[2])

def read_readings(path: Path) -> List[CounterReading]:
    readings = []
    handler = ErrorHandler()
    if not path.is_file(): return readings
    
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            try: readings.append(parse_line(line))
            except Exception as e: handler.print_warning(f"Строка {i}: {e}")
    return readings

def save_readings(path: Path, readings: List[CounterReading]):
    with path.open("w", encoding="utf-8") as f:
        for r in readings:
            f.write(f'"{r.resource_type}" {r.date:%Y.%m.%d} {r.value:.2f} {r.quality}\n')
