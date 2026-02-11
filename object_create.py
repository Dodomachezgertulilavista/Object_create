from datetime import datetime

class CounterReading:
    def __init__(self, resource_type, date_obj, value):
        self.resource_type = resource_type
        self.date = date_obj
        self.value = value

    def __str__(self):
        return (f"\nОбъект сформирован:\n"
                f"Тип ресурса: {self.resource_type}\n"
                f"Дата: {self.date.strftime('%d.%m.%Y')}\n"
                f"Значение: {self.value:.2f}")

def get_valid_object():
    while True:
        user_input = input("Введите описание объекта: ").strip()
        try:
            parts = user_input.split('"')
            if len(parts) < 3:
                raise ValueError("Тип ресурса должен быть в кавычках.")

            resource_name = parts[1]
            remaining_data = parts[2].strip().split()
            
            if len(remaining_data) < 2:
                raise ValueError("Не найдены дата или значение.")

            date_str = remaining_data[0]
            value_str = remaining_data[1]

            valid_date = datetime.strptime(date_str, "%Y.%m.%d").date()
            valid_value = float(value_str.replace(',', '.'))

            return CounterReading(resource_name, valid_date, valid_value)

        except Exception as e:
            print(f"Ошибка парсинга: {e}. Попробуйте снова.")

if __name__ == "__main__":
    result = get_valid_object()
    print(result)