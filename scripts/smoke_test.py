#!/usr/bin/env python3
"""Teste rápido da API. Execute com o backend já iniciado."""
import json
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:8000"


def call(path, method="GET", body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = Request(BASE + path, data=data, method=method, headers=headers)
    with urlopen(req, timeout=5) as response:
        return response.status, json.loads(response.read().decode())


status, health = call("/api/health")
assert status == 200 and health["status"] == "ok"

status, login = call("/api/login", "POST", {"email": "maria@agendasaude.demo", "password": "123456"})
assert status == 200 and login.get("token")

token = login["token"]
status, doctors = call("/api/doctors")
assert status == 200 and len(doctors["doctors"]) >= 1

status, appointments = call("/api/appointments", token=token)
assert status == 200 and "appointments" in appointments

print("Smoke test concluído: health, login, doctors e appointments OK.")
