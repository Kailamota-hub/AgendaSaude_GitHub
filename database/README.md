# Banco de dados

A prova de conceito utiliza **SQLite**.

- `schema.sql`: estrutura das tabelas, chaves estrangeiras e índices.
- `seed.sql`: carga inicial dos profissionais e especialidades.
- `agendasaude.db`: é criado automaticamente ao iniciar o backend e, por isso, não precisa ser versionado.

O backend também cria automaticamente o usuário de demonstração:

- E-mail: `maria@agendasaude.demo`
- Senha: `123456`

As senhas são armazenadas usando PBKDF2-HMAC-SHA256 com salt individual. A autenticação desta prova de conceito usa token em memória e deve ser substituída por uma solução persistente/robusta em ambiente de produção.
