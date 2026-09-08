"""Testes das restrições de integridade do banco de dados de consultas."""
from __future__ import annotations

import sqlite3
import unittest
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "database" / "schema.sql"


class ActiveSlotConstraintTest(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.conn.execute(
            "INSERT INTO users (id, name, email, password_salt, password_hash) "
            "VALUES (1, 'Paciente 1', 'paciente1@teste.com', 'aa', 'bb'), "
            "       (2, 'Paciente 2', 'paciente2@teste.com', 'cc', 'dd')"
        )
        self.conn.execute(
            "INSERT INTO doctors (id, name, specialty, active) "
            "VALUES (1, 'Dra. Ana', 'Clínica Geral', 1), "
            "       (2, 'Dr. Bruno', 'Cardiologia', 1)"
        )
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def _insert_appointment(
        self,
        user_id: int,
        doctor_id: int = 1,
        appointment_date: str = "2099-01-01",
        appointment_time: str = "08:00",
        status: str = "AGENDADA",
    ) -> int:
        cursor = self.conn.execute(
            "INSERT INTO appointments "
            "(user_id, doctor_id, appointment_date, appointment_time, status) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, doctor_id, appointment_date, appointment_time, status),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def test_rejeita_dois_agendamentos_ativos_no_mesmo_horario(self):
        self._insert_appointment(user_id=1)

        with self.assertRaises(sqlite3.IntegrityError):
            self._insert_appointment(user_id=2)

    def test_consulta_cancelada_nao_bloqueia_novo_agendamento(self):
        self._insert_appointment(user_id=1, status="CANCELADA")

        appointment_id = self._insert_appointment(user_id=2)

        self.assertGreater(appointment_id, 0)

    def test_permite_mesmo_horario_para_profissionais_diferentes(self):
        self._insert_appointment(user_id=1, doctor_id=1)

        appointment_id = self._insert_appointment(user_id=2, doctor_id=2)

        self.assertGreater(appointment_id, 0)

    def test_rejeita_reagendamento_para_horario_ocupado(self):
        self._insert_appointment(user_id=1, appointment_time="08:00")
        second_id = self._insert_appointment(user_id=2, appointment_time="09:00")

        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "UPDATE appointments SET appointment_time = '08:00' WHERE id = ?",
                (second_id,),
            )


if __name__ == "__main__":
    unittest.main()
