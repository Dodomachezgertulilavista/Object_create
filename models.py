import dataclasses
from datetime import date

@dataclasses.dataclass(frozen=True)
class CounterReading:
    resource_type: str
    date: date
    value: float
    quality: str

    def __str__(self) -> str:
        return f"{self.resource_type} | {self.date} | {self.value} | {self.quality}"

def parse_reading_parts(res_type: str, date_str: str, val_str: str, quality: str = "Норма") -> CounterReading:
    dt = date.fromisoformat(date_str.replace(".", "-"))
    val = float(val_str.replace(",", "."))
    return CounterReading(res_type.strip(), dt, val, quality.strip())
