"""Testes das validações puras do handler: _parse_positive_int, _valid_date,
_validate_appointment_fields e row_to_dict."""
from __future__ import annotations

import sqlite3
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

import app  # noqa: E402

Handler = app.AgendaSaudeHandler


class ParsePositiveIntTest(unittest.TestCase):
    def test_aceita_inteiros_positivos(self):
        self.assertEqual(Handler._parse_positive_int(5), 5)
        self.assertEqual(Handler._parse_positive_int("42"), 42)

    def test_rejeita_zero_e_negativos(self):
        self.assertIsNone(Handler._parse_positive_int(0))
        self.assertIsNone(Handler._parse_positive_int(-3))
        self.assertIsNone(Handler._parse_positive_int("-1"))

    def test_rejeita_valores_invalidos(self):
        self.assertIsNone(Handler._parse_positive_int("abc"))
        self.assertIsNone(Handler._parse_positive_int(""))
        self.assertIsNone(Handler._parse_positive_int(None))


class ValidDateTest(unittest.TestCase):
    def test_aceita_data_de_hoje(self):
        hoje = date.today().isoformat()
        self.assertTrue(Handler._valid_date(hoje))

    def test_aceita_data_futura(self):
        futuro = (date.today() + timedelta(days=10)).isoformat()
        self.assertTrue(Handler._valid_date(futuro))

    def test_rejeita_data_passada(self):
        ontem = (date.today() - timedelta(days=1)).isoformat()
        self.assertFalse(Handler._valid_date(ontem))

    def test_rejeita_formato_invalido(self):
        self.assertFalse(Handler._valid_date("07/09/2026"))
        self.assertFalse(Handler._valid_date("data-invalida"))
        self.assertFalse(Handler._valid_date(""))


class ValidateAppointmentFieldsTest(unittest.TestCase):
    def setUp(self):
        # Instancia o handler sem passar pelo __init__ (que exigiria socket).
        self.handler = object.__new__(Handler)
        self.data_valida = (date.today() + timedelta(days=1)).isoformat()

    def test_campos_validos_retornam_none(self):
        erro = self.handler._validate_appointment_fields(1, self.data_valida, "08:00")
        self.assertIsNone(erro)

    def test_doctor_id_ausente(self):
        erro = self.handler._validate_appointment_fields(None, self.data_valida, "08:00")
        self.assertEqual(erro, "Selecione um profissional.")

    def test_data_invalida(self):
        erro = self.handler._validate_appointment_fields(1, "2000-01-01", "08:00")
        self.assertEqual(erro, "Selecione uma data válida a partir de hoje.")

    def test_horario_fora_da_lista(self):
        erro = self.handler._validate_appointment_fields(1, self.data_valida, "07:30")
        self.assertEqual(erro, "Selecione um horário válido.")

    def test_todos_horarios_disponiveis_sao_aceitos(self):
        for horario in app.AVAILABLE_TIMES:
            with self.subTest(horario=horario):
                erro = self.handler._validate_appointment_fields(1, self.data_valida, horario)
                self.assertIsNone(erro)


class RowToDictTest(unittest.TestCase):
    def test_none_retorna_none(self):
        self.assertIsNone(app.row_to_dict(None))

    def test_converte_row_em_dict(self):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT 1 AS id, 'Maria' AS name").fetchone()
        self.assertEqual(app.row_to_dict(row), {"id": 1, "name": "Maria"})
        conn.close()


if __name__ == "__main__":
    unittest.main()
