# Testes unitários — AgendaSaúde

Testes das regras de negócio do backend, escritos com o módulo `unittest`
da biblioteca padrão (sem dependências externas, seguindo a filosofia do projeto).

## Como executar

A partir da raiz do repositório:

```bash
python -m unittest discover -s tests -v
```

Os testes **não** exigem o servidor no ar nem criam o banco `agendasaude.db`:
usam SQLite em memória e funções puras isoladas.

## Cobertura atual

| Arquivo | O que cobre |
|---------|-------------|
| `test_password.py` | `password_hash` / `verify_password` — determinismo do salt, verificação de senha correta/incorreta |
| `test_validation.py` | `_parse_positive_int`, `_valid_date`, `_validate_appointment_fields`, `row_to_dict` |
| `test_slots.py` | `_slot_is_booked` — conflito de horário, `status = CANCELADA` ignorado, `ignore_id` no reagendamento |
