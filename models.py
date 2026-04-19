"""Модуль с моделью данных для показаний счётчиков."""

import dataclasses
from datetime import date


@dataclasses.dataclass(frozen=True)
class CounterReading:
  """Представляет одно показание счётчика.

  Attributes:
    resource_type: Название ресурса.
    date: Объект даты замера.
    value: Числовое значение показания.
  """

  resource_type: str
  date: date
  value: float

  def __str__(self) -> str:
    return (
        f"Тип ресурса: {self.resource_type}\n"
        f"Дата:       {self.date:%d.%m.%Y}\n"
        f"Значение:   {self.value:,.2f}"
    )


def parse_reading_parts(
    resource_type: str,
    date_str: str,
    value_str: str,
) -> CounterReading:
  """Создаёт объект CounterReading из строковых компонентов.

  Args:
    resource_type: Название ресурса (например, "Горячая вода").
    date_str: Дата в формате YYYY.MM.DD или YYYY-MM-DD.
    value_str: Значение с возможной запятой как разделителем.

  Returns:
    Готовый объект CounterReading.

  Raises:
    ValueError: Некорректный формат даты или значения.
  """
  normalized_date = date_str.replace(".", "-")
  dt = date.fromisoformat(normalized_date)
  value = float(value_str.replace(",", "."))

  return CounterReading(resource_type, dt, value)