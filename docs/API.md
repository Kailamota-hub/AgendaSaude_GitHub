# API REST - AgendaSaúde

Base local: `http://127.0.0.1:8000`

| Método | Rota | Autenticação | Finalidade |
|---|---|---|---|
| GET | `/api/health` | Não | Verifica se o backend está ativo. |
| POST | `/api/register` | Não | Cria um paciente. |
| POST | `/api/login` | Não | Autentica e retorna token de sessão. |
| POST | `/api/logout` | Sim | Encerra a sessão. |
| GET | `/api/me` | Sim | Retorna o paciente autenticado. |
| GET | `/api/doctors` | Não | Lista profissionais e especialidades. |
| GET | `/api/slots?doctor_id=1&date=AAAA-MM-DD` | Não | Lista horários ainda livres. |
| GET | `/api/appointments` | Sim | Lista histórico do paciente. |
| POST | `/api/appointments` | Sim | Agenda nova consulta. |
| PUT | `/api/appointments/{id}` | Sim | Reagenda consulta ativa. |
| DELETE | `/api/appointments/{id}` | Sim | Cancela consulta ativa. |

## Exemplo de agendamento

```json
{
  "doctor_id": 1,
  "date": "2026-09-10",
  "time": "09:00"
}
```

## Observação de segurança

A senha é armazenada com hash PBKDF2-HMAC-SHA256 e salt individual. Para simplificar a prova de conceito, os tokens de sessão são mantidos apenas em memória; em produção, a autenticação deve usar uma estratégia persistente, com expiração de sessão, HTTPS e controles adicionais de segurança.
