"""Testes da regra de conflito de horários (_slot_is_booked), usando um banco
SQLite em memória para isolar a lógica do restante do servidor."""
from __future__ import annotations

import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

import app  # noqa: E402

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "database" / "schema.sql"


class SlotIsBookedTest(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        # Dados mínimos: um usuário e um profissional.
        self.conn.execute(
            "INSERT INTO users (id, name, email, password_salt, password_hash) "
            "VALUES (1, 'Teste', 'teste@ex.com', 'aa', 'bb')"
        )
        self.conn.execute(
            "INSERT INTO doctors (id, name, specialty, active) VALUES (1, 'Dra. Ana', 'Clínica', 1)"
        )
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def _agendar(self, data="2099-01-01", hora="08:00", status="AGENDADA"):
        cur = self.conn.execute(
            "INSERT INTO appointments (user_id, doctor_id, appointment_date, appointment_time, status) "
            "VALUES (1, 1, ?, ?, ?)",
            (data, hora, status),
        )
        self.conn.commit()
        return cur.lastrowid

    def test_horario_livre_nao_esta_ocupado(self):
        self.assertFalse(app.AgendaSaudeHandler._slot_is_booked(self.conn, 1, "2099-01-01", "08:00"))

    def test_horario_agendado_esta_ocupado(self):
        self._agendar(hora="08:00")
        self.assertTrue(app.AgendaSaudeHandler._slot_is_booked(self.conn, 1, "2099-01-01", "08:00"))

    def test_horario_cancelado_nao_conta_como_ocupado(self):
        self._agendar(hora="08:00", status="CANCELADA")
        self.assertFalse(app.AgendaSaudeHandler._slot_is_booked(self.conn, 1, "2099-01-01", "08:00"))

    def test_outra_data_ou_horario_nao_conflita(self):
        self._agendar(data="2099-01-01", hora="08:00")
        self.assertFalse(app.AgendaSaudeHandler._slot_is_booked(self.conn, 1, "2099-01-02", "08:00"))
        self.assertFalse(app.AgendaSaudeHandler._slot_is_booked(self.conn, 1, "2099-01-01", "09:00"))

    def test_ignore_id_permite_reagendar_o_proprio_horario(self):
        appt_id = self._agendar(hora="08:00")
        # Sem ignore_id, o próprio registro conta como conflito...
        self.assertTrue(app.AgendaSaudeHandler._slot_is_booked(self.conn, 1, "2099-01-01", "08:00"))
        # ...mas ao ignorar o próprio id (caso de reagendamento), não há conflito.
        self.assertFalse(
            app.AgendaSaudeHandler._slot_is_booked(self.conn, 1, "2099-01-01", "08:00", ignore_id=appt_id)
        )


if __name__ == "__main__":
    unittest.main()
