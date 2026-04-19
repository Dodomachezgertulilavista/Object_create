"""Модуль для обработки файлов скриптов команд (ADD, REM, SAVE)."""

import re
import operator
from datetime import date
from pathlib import Path
from typing import List

from models import CounterReading, parse_reading_parts
from error_handler import ErrorHandler
from file_io import save_readings

# Словарь для конвертации строковых операторов в функции Python
OPERATORS = {
    '==': operator.eq,
    '!=': operator.ne,
    '<': operator.lt,
    '<=': operator.le,
    '>': operator.gt,
    '>=': operator.ge
}

def _evaluate_condition(reading: CounterReading, condition: str) -> bool:
    """Оценивает, соответствует ли объект CounterReading текстовому условию."""
    # Ожидаемый формат: "поле оператор значение" (например, "value < 1000")
    match = re.match(r"^\s*(value|date|resource|resource_type)\s*(==|!=|<=|>=|<|>)\s*(.+)\s*$", condition)
    if not match:
        raise ValueError(f"Неизвестный формат условия: '{condition}'")
        
    field, op_str, val_str = match.groups()
    op_func = OPERATORS[op_str]
    
    if field == 'value':
        val = float(val_str.replace(',', '.'))
        return op_func(reading.value, val)
    
    elif field == 'date':
        val = date.fromisoformat(val_str.replace('.', '-'))
        return op_func(reading.date, val)
    
    elif field in ('resource', 'resource_type'):
        val = val_str.strip('"\' ') # Убираем кавычки, если они есть
        return op_func(reading.resource_type, val)
        
    return False


def execute_commands(script_path: Path, readings: List[CounterReading]) -> None:
    """Выполняет скрипт команд построчно над переданным списком данных."""
    handler = ErrorHandler()
    handler.print_info(f"--- Запуск скрипта: {script_path.name} ---")
    
    try:
        with script_path.open(encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                    
                try:
                    # КОМАНДА ADD
                    if line.startswith("ADD "):
                        args = line[4:].split(';')
                        if len(args) != 3:
                            raise ValueError("ADD требует 3 аргумента через ';' (ресурс; дата; значение)")
                        
                        new_r = parse_reading_parts(args[0].strip(), args[1].strip(), args[2].strip())
                        readings.append(new_r)
                        handler.print_info(f"[{i}] ADD: добавлено '{new_r.resource_type}' = {new_r.value}")
                        
                    # КОМАНДА REM
                    elif line.startswith("REM "):
                        condition = line[4:].strip()
                        original_len = len(readings)
                        # Перезаписываем список (фильтруем те, которые НЕ подходят под условие REM)
                        readings[:] = [r for r in readings if not _evaluate_condition(r, condition)]
                        removed = original_len - len(readings)
                        handler.print_info(f"[{i}] REM: удалено записей: {removed} по условию '{condition}'")
                        
                    # КОМАНДА SAVE
                    elif line.startswith("SAVE "):
                        filename = line[5:].strip()
                        # Сохраняем текущее состояние в указанный файл
                        save_readings(Path(filename), readings)
                        handler.print_info(f"[{i}] SAVE: данные успешно экспортированы в '{filename}'")
                        
                    else:
                        handler.print_warning(f"[{i}] Неизвестная команда: '{line}'")
                        
                except Exception as e:
                    handler.print_error(f"[{i}] Ошибка выполнения команды: {e}")
                    
    except Exception as e:
        handler.print_error(f"Не удалось прочитать файл скрипта {script_path}: {e}")
        
    handler.print_info("--- Завершение работы скрипта ---")