# Arquitetura da prova de conceito

```text
Navegador
  |
  |  HTML/CSS/JavaScript + fetch()
  v
Servidor Python (HTTP + API REST)
  |
  |  sqlite3
  v
Banco SQLite
```

## Frontend

O frontend foi criado com HTML5, CSS3 e JavaScript puro. Ele contempla a jornada escolhida na primeira etapa: acesso, cadastro/login, escolha da consulta, confirmação e acompanhamento. Também permite cancelamento e reagendamento.

## Backend

O backend foi desenvolvido em Python 3 com `http.server`, `sqlite3`, `hashlib` e outras bibliotecas nativas. Ele disponibiliza endpoints REST, faz validações, autentica o usuário, verifica conflito de horários e persiste as consultas.

## Banco de dados

O banco SQLite contém três entidades principais:

- `users`: pacientes cadastrados;
- `doctors`: profissionais e especialidades;
- `appointments`: consultas e seu status.

A estrutura está em `database/schema.sql` e a carga inicial em `database/seed.sql`.

Uma restrição única parcial protege cada combinação de profissional, data e horário enquanto a consulta estiver com status `AGENDADA`. Assim, o próprio banco impede reservas duplicadas mesmo quando duas requisições chegam simultaneamente. Consultas `CANCELADA` não bloqueiam uma nova reserva para o mesmo horário.
