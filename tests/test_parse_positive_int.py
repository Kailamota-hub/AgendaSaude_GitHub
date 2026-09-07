"""Testes unitários — validação de identificadores (_parse_positive_int).

Cobre a conversão de valores recebidos via query string ou corpo JSON
para inteiros positivos, usada em doctor_id e appointment_id.
Escrito com o módulo `unittest` da biblioteca padrão, sem dependências
externas, seguindo a filosofia do projeto.
"""
import importlib.util
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
APP_PATH = BACKEND_DIR / "app.py"

spec = importlib.util.spec_from_file_location("agendasaude_app", APP_PATH)
agendasaude_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agendasaude_app)

parse_positive_int = agendasaude_app.AgendaSaudeHandler._parse_positive_int


class TestParsePositiveInt(unittest.TestCase):
    def test_valid_integer_string(self):
        self.assertEqual(parse_positive_int("5"), 5)

    def test_valid_integer(self):
        self.assertEqual(parse_positive_int(10), 10)

    def test_zero_is_invalid(self):
        self.assertIsNone(parse_positive_int("0"))

    def test_negative_is_invalid(self):
        self.assertIsNone(parse_positive_int("-3"))

    def test_none_is_invalid(self):
        self.assertIsNone(parse_positive_int(None))

    def test_empty_string_is_invalid(self):
        self.assertIsNone(parse_positive_int(""))

    def test_non_numeric_string_is_invalid(self):
        self.assertIsNone(parse_positive_int("abc"))

    def test_float_string_is_invalid(self):
        self.assertIsNone(parse_positive_int("1.5"))


if __name__ == "__main__":
    unittest.main()