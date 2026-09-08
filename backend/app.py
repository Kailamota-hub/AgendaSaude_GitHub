#!/usr/bin/env python3
"""AgendaSaúde - API e servidor web da prova de conceito.

Executa somente com bibliotecas nativas do Python 3.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import mimetypes
import os
import secrets
import sqlite3
from datetime import date
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
DATABASE_DIR = ROOT_DIR / "database"
DB_PATH = DATABASE_DIR / "agendasaude.db"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"
SEED_PATH = DATABASE_DIR / "seed.sql"
HOST = os.environ.get("AGENDA_HOST", "127.0.0.1")
PORT = int(os.environ.get("AGENDA_PORT", "8000"))

# Sessões em memória: adequadas apenas para esta prova de conceito.
SESSIONS: dict[str, int] = {}
AVAILABLE_TIMES = ["08:00", "09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00"]


def db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def password_hash(password: str, salt_hex: str | None = None) -> tuple[str, str]:
    salt = bytes.fromhex(salt_hex) if salt_hex else secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return salt.hex(), digest.hex()


def verify_password(password: str, salt_hex: str, expected_hash: str) -> bool:
    _, actual_hash = password_hash(password, salt_hex)
    return hmac.compare_digest(actual_hash, expected_hash)


def initialize_database() -> None:
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    with db_connection() as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.executescript(SEED_PATH.read_text(encoding="utf-8"))
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?", ("maria@agendasaude.demo",)
        ).fetchone()
        if not existing:
            salt, hashed = password_hash("123456")
            conn.execute(
                "INSERT INTO users (name, email, password_salt, password_hash) VALUES (?, ?, ?, ?)",
                ("Maria Aparecida Santos", "maria@agendasaude.demo", salt, hashed),
            )
        conn.commit()


def row_to_dict(row: sqlite3.Row | None) -> dict | None:
    return dict(row) if row is not None else None


class AgendaSaudeHandler(BaseHTTPRequestHandler):
    server_version = "AgendaSaudePOC/1.0"

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{self.log_date_time_string()}] {self.client_address[0]} - {fmt % args}")

    def _send_json(self, payload: dict | list, status: int = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _send_error_json(self, message: str, status: int = HTTPStatus.BAD_REQUEST) -> None:
        self._send_json({"error": message}, status)

    def _read_json(self) -> dict:
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        if content_length <= 0:
            return {}
        raw = self.rfile.read(content_length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError("JSON inválido.") from exc
        if not isinstance(data, dict):
            raise ValueError("O corpo da requisição deve ser um objeto JSON.")
        return data

    def _current_user_id(self) -> int | None:
        auth = self.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return None
        return SESSIONS.get(auth.removeprefix("Bearer ").strip())

    def _require_user(self) -> int | None:
        user_id = self._current_user_id()
        if user_id is None:
            self._send_error_json("Autenticação necessária.", HTTPStatus.UNAUTHORIZED)
        return user_id

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/api/health":
            self._send_json({"status": "ok", "service": "AgendaSaúde"})
            return

        if path == "/api/me":
            user_id = self._require_user()
            if user_id is None:
                return
            with db_connection() as conn:
                user = conn.execute(
                    "SELECT id, name, email, created_at FROM users WHERE id = ?", (user_id,)
                ).fetchone()
            self._send_json({"user": row_to_dict(user)})
            return

        if path == "/api/doctors":
            with db_connection() as conn:
                rows = conn.execute(
                    "SELECT id, name, specialty FROM doctors WHERE active = 1 ORDER BY specialty, name"
                ).fetchall()
            self._send_json({"doctors": [dict(row) for row in rows]})
            return

        if path == "/api/slots":
            doctor_id = self._parse_positive_int(query.get("doctor_id", [""])[0])
            selected_date = query.get("date", [""])[0]
            if not doctor_id or not self._valid_date(selected_date):
                self._send_error_json("Informe doctor_id e date no formato AAAA-MM-DD.")
                return
            with db_connection() as conn:
                doctor = conn.execute(
                    "SELECT id FROM doctors WHERE id = ? AND active = 1", (doctor_id,)
                ).fetchone()
                if not doctor:
                    self._send_error_json("Profissional não encontrado.", HTTPStatus.NOT_FOUND)
                    return
                booked = {
                    row["appointment_time"]
                    for row in conn.execute(
                        """SELECT appointment_time FROM appointments
                           WHERE doctor_id = ? AND appointment_date = ? AND status = 'AGENDADA'""",
                        (doctor_id, selected_date),
                    ).fetchall()
                }
            slots = [time for time in AVAILABLE_TIMES if time not in booked]
            self._send_json({"date": selected_date, "doctor_id": doctor_id, "slots": slots})
            return

        if path == "/api/appointments":
            user_id = self._require_user()
            if user_id is None:
                return
            with db_connection() as conn:
                rows = conn.execute(
                    """SELECT a.id, a.appointment_date, a.appointment_time, a.status,
                              a.created_at, a.updated_at,
                              d.id AS doctor_id, d.name AS doctor_name, d.specialty
                       FROM appointments a
                       JOIN doctors d ON d.id = a.doctor_id
                       WHERE a.user_id = ?
                       ORDER BY a.appointment_date DESC, a.appointment_time DESC, a.id DESC""",
                    (user_id,),
                ).fetchall()
            self._send_json({"appointments": [dict(row) for row in rows]})
            return

        if path.startswith("/api/"):
            self._send_error_json("Rota não encontrada.", HTTPStatus.NOT_FOUND)
            return

        self._serve_static(path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            body = self._read_json()
        except ValueError as exc:
            self._send_error_json(str(exc))
            return

        if path == "/api/register":
            self._register(body)
            return
        if path == "/api/login":
            self._login(body)
            return
        if path == "/api/logout":
            auth = self.headers.get("Authorization", "")
            if auth.startswith("Bearer "):
                SESSIONS.pop(auth.removeprefix("Bearer ").strip(), None)
            self._send_json({"message": "Sessão encerrada."})
            return
        if path == "/api/appointments":
            user_id = self._require_user()
            if user_id is None:
                return
            self._create_appointment(user_id, body)
            return

        self._send_error_json("Rota não encontrada.", HTTPStatus.NOT_FOUND)

    def do_PUT(self) -> None:
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/api/appointments/"):
            self._send_error_json("Rota não encontrada.", HTTPStatus.NOT_FOUND)
            return
        user_id = self._require_user()
        if user_id is None:
            return
        appointment_id = self._parse_positive_int(parsed.path.rsplit("/", 1)[-1])
        if not appointment_id:
            self._send_error_json("Identificador de consulta inválido.")
            return
        try:
            body = self._read_json()
        except ValueError as exc:
            self._send_error_json(str(exc))
            return
        self._reschedule_appointment(user_id, appointment_id, body)

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/api/appointments/"):
            self._send_error_json("Rota não encontrada.", HTTPStatus.NOT_FOUND)
            return
        user_id = self._require_user()
        if user_id is None:
            return
        appointment_id = self._parse_positive_int(parsed.path.rsplit("/", 1)[-1])
        if not appointment_id:
            self._send_error_json("Identificador de consulta inválido.")
            return
        with db_connection() as conn:
            cur = conn.execute(
                """UPDATE appointments
                   SET status = 'CANCELADA', updated_at = CURRENT_TIMESTAMP
                   WHERE id = ? AND user_id = ? AND status = 'AGENDADA'""",
                (appointment_id, user_id),
            )
            conn.commit()
        if cur.rowcount == 0:
            self._send_error_json("Consulta ativa não encontrada.", HTTPStatus.NOT_FOUND)
            return
        self._send_json({"message": "Consulta cancelada com sucesso."})

    def _register(self, body: dict) -> None:
        name = str(body.get("name", "")).strip()
        email = str(body.get("email", "")).strip().lower()
        password = str(body.get("password", ""))
        if len(name) < 3:
            self._send_error_json("Informe um nome válido.")
            return
        if "@" not in email or "." not in email:
            self._send_error_json("Informe um e-mail válido.")
            return
        if len(password) < 6:
            self._send_error_json("A senha deve ter pelo menos 6 caracteres.")
            return
        salt, hashed = password_hash(password)
        try:
            with db_connection() as conn:
                cur = conn.execute(
                    "INSERT INTO users (name, email, password_salt, password_hash) VALUES (?, ?, ?, ?)",
                    (name, email, salt, hashed),
                )
                conn.commit()
                user_id = cur.lastrowid
        except sqlite3.IntegrityError:
            self._send_error_json("Este e-mail já está cadastrado.", HTTPStatus.CONFLICT)
            return
        token = secrets.token_urlsafe(32)
        SESSIONS[token] = int(user_id)
        self._send_json({"token": token, "user": {"id": user_id, "name": name, "email": email}}, HTTPStatus.CREATED)

    def _login(self, body: dict) -> None:
        email = str(body.get("email", "")).strip().lower()
        password = str(body.get("password", ""))
        with db_connection() as conn:
            row = conn.execute(
                "SELECT id, name, email, password_salt, password_hash FROM users WHERE email = ?",
                (email,),
            ).fetchone()
        if not row or not verify_password(password, row["password_salt"], row["password_hash"]):
            self._send_error_json("E-mail ou senha inválidos.", HTTPStatus.UNAUTHORIZED)
            return
        token = secrets.token_urlsafe(32)
        SESSIONS[token] = int(row["id"])
        self._send_json({
            "token": token,
            "user": {"id": row["id"], "name": row["name"], "email": row["email"]},
        })

    def _create_appointment(self, user_id: int, body: dict) -> None:
        doctor_id = self._parse_positive_int(body.get("doctor_id"))
        selected_date = str(body.get("date", "")).strip()
        selected_time = str(body.get("time", "")).strip()
        error = self._validate_appointment_fields(doctor_id, selected_date, selected_time)
        if error:
            self._send_error_json(error)
            return
        try:
            with db_connection() as conn:
                if not conn.execute("SELECT 1 FROM doctors WHERE id = ? AND active = 1", (doctor_id,)).fetchone():
                    self._send_error_json("Profissional não encontrado.", HTTPStatus.NOT_FOUND)
                    return
                if self._slot_is_booked(conn, doctor_id, selected_date, selected_time):
                    self._send_error_json("Horário indisponível. Escolha outro horário.", HTTPStatus.CONFLICT)
                    return
                cur = conn.execute(
                    """INSERT INTO appointments (user_id, doctor_id, appointment_date, appointment_time, status)
                       VALUES (?, ?, ?, ?, 'AGENDADA')""",
                    (user_id, doctor_id, selected_date, selected_time),
                )
                conn.commit()
        except sqlite3.IntegrityError:
            self._send_error_json("Horário indisponível. Escolha outro horário.", HTTPStatus.CONFLICT)
            return
        self._send_json({"message": "Consulta agendada com sucesso.", "appointment_id": cur.lastrowid}, HTTPStatus.CREATED)

    def _reschedule_appointment(self, user_id: int, appointment_id: int, body: dict) -> None:
        doctor_id = self._parse_positive_int(body.get("doctor_id"))
        selected_date = str(body.get("date", "")).strip()
        selected_time = str(body.get("time", "")).strip()
        error = self._validate_appointment_fields(doctor_id, selected_date, selected_time)
        if error:
            self._send_error_json(error)
            return
        try:
            with db_connection() as conn:
                current = conn.execute(
                    "SELECT id FROM appointments WHERE id = ? AND user_id = ? AND status = 'AGENDADA'",
                    (appointment_id, user_id),
                ).fetchone()
                if not current:
                    self._send_error_json("Consulta ativa não encontrada.", HTTPStatus.NOT_FOUND)
                    return
                if not conn.execute("SELECT 1 FROM doctors WHERE id = ? AND active = 1", (doctor_id,)).fetchone():
                    self._send_error_json("Profissional não encontrado.", HTTPStatus.NOT_FOUND)
                    return
                if self._slot_is_booked(conn, doctor_id, selected_date, selected_time, ignore_id=appointment_id):
                    self._send_error_json("Horário indisponível. Escolha outro horário.", HTTPStatus.CONFLICT)
                    return
                conn.execute(
                    """UPDATE appointments
                       SET doctor_id = ?, appointment_date = ?, appointment_time = ?, updated_at = CURRENT_TIMESTAMP
                       WHERE id = ? AND user_id = ?""",
                    (doctor_id, selected_date, selected_time, appointment_id, user_id),
                )
                conn.commit()
        except sqlite3.IntegrityError:
            self._send_error_json("Horário indisponível. Escolha outro horário.", HTTPStatus.CONFLICT)
            return
        self._send_json({"message": "Consulta reagendada com sucesso."})

    @staticmethod
    def _slot_is_booked(
        conn: sqlite3.Connection,
        doctor_id: int,
        selected_date: str,
        selected_time: str,
        ignore_id: int | None = None,
    ) -> bool:
        sql = """SELECT 1 FROM appointments
                 WHERE doctor_id = ? AND appointment_date = ? AND appointment_time = ?
                   AND status = 'AGENDADA'"""
        params: list[object] = [doctor_id, selected_date, selected_time]
        if ignore_id is not None:
            sql += " AND id <> ?"
            params.append(ignore_id)
        return conn.execute(sql, tuple(params)).fetchone() is not None

    @staticmethod
    def _parse_positive_int(value) -> int | None:
        try:
            number = int(value)
            return number if number > 0 else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _valid_date(value: str) -> bool:
        try:
            parsed = date.fromisoformat(value)
            return parsed >= date.today()
        except ValueError:
            return False

    def _validate_appointment_fields(self, doctor_id: int | None, selected_date: str, selected_time: str) -> str | None:
        if not doctor_id:
            return "Selecione um profissional."
        if not self._valid_date(selected_date):
            return "Selecione uma data válida a partir de hoje."
        if selected_time not in AVAILABLE_TIMES:
            return "Selecione um horário válido."
        return None

    def _serve_static(self, requested_path: str) -> None:
        relative = "index.html" if requested_path in ("/", "") else requested_path.lstrip("/")
        candidate = (FRONTEND_DIR / relative).resolve()
        try:
            candidate.relative_to(FRONTEND_DIR.resolve())
        except ValueError:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if not candidate.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content = candidate.read_bytes()
        content_type, _ = mimetypes.guess_type(candidate.name)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", (content_type or "application/octet-stream") + ("; charset=utf-8" if (content_type or "").startswith("text/") else ""))
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main() -> None:
    initialize_database()
    server = ThreadingHTTPServer((HOST, PORT), AgendaSaudeHandler)
    print(f"AgendaSaúde disponível em http://{HOST}:{PORT}")
    print("Para encerrar, pressione Ctrl+C.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
