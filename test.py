import unittest
from models import parse_reading_parts

class TestLab(unittest.TestCase):
    def test_quality(self):
        r = parse_reading_parts("Вода", "2024-01-01", "10", "Высокое")
        self.assertEqual(r.quality, "Высокое")
    def test_invalid_date_format(self):
        """Специально ломаем формат даты."""
        with self.assertRaises(ValueError):
            parse_reading_parts("Свет", "вчера", "100", "Норма")


if __name__ == "__main__":
    unittest.main()
