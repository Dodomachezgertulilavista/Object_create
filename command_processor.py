import re, operator
from pathlib import Path
from typing import List
from models import CounterReading, parse_reading_parts
from error_handler import ErrorHandler
from file_io import save_readings

def _evaluate(r: CounterReading, cond: str) -> bool:
    m = re.match(r"^\s*(value|quality|resource)\s*(==|!=|<=|>=|<|>)\s*(.+)\s*$", cond)
    if not m: return False
    field, op, val = m.groups()
    ops = {"==":operator.eq, "!=":operator.ne, "<":operator.lt, "<=":operator.le, ">":operator.gt, ">=":operator.ge}
    
    if field == "value": return ops[op](r.value, float(val))
    if field == "quality": return ops[op](r.quality, val.strip())
    if field == "resource": return ops[op](r.resource_type, val.strip())
    return False

def execute_commands(path: Path, readings: List[CounterReading]):
    handler = ErrorHandler()
    handler.print_info(f"Запуск скрипта: {path.name}")
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"): continue
            try:
                if line.startswith("ADD "):
                    args = line[4:].split(";")
                    new_r = parse_reading_parts(args[0], args[1], args[2], args[3])
                    readings.append(new_r)
                elif line.startswith("REM "):
                    cond = line[4:].strip()
                    readings[:] = [r for r in readings if not _evaluate(r, cond)]
                elif line.startswith("SAVE "):
                    save_readings(Path(line[5:].strip()), readings)
            except Exception as e:
                handler.print_error(f"Линия {i}: {e}")
