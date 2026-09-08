# AgendaSaúde

Prova de conceito do **Projeto Integrador - Segunda Etapa** do curso de Tecnologia em Análise e Desenvolvimento de Sistemas / TSI do SENAC.

O projeto dá continuidade à primeira entrega, na qual foram definidos a visão do produto, o problema, o público-alvo, os stakeholders, as personas e a jornada do usuário. Nesta etapa, a jornada da paciente **Maria Aparecida Santos** foi transformada em uma aplicação funcional.

## Prova de conceito escolhida

O fluxo implementado é:

**Acesso → cadastro/login → escolha do profissional → escolha de data e horário → confirmação → acompanhamento → cancelamento/reagendamento.**

A escolha está alinhada ao problema central identificado na primeira etapa: reduzir filas, retrabalho, conflitos de horários e dificuldade de acesso ao agendamento.

## Funcionalidades implementadas

- cadastro de paciente;
- login com senha armazenada por hash;
- listagem de especialidades e profissionais;
- consulta de horários disponíveis;
- agendamento de consultas;
- bloqueio de conflito de horário para o mesmo profissional;
- histórico do paciente;
- cancelamento de consulta;
- reagendamento;
- indicadores de consultas agendadas e canceladas;
- interface responsiva para desktop e celular.

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Frontend | HTML5, CSS3 e JavaScript |
| Backend | Python 3 - bibliotecas nativas |
| Banco de dados | SQLite |
| Comunicação | API REST / JSON |
| Versionamento | Git e GitHub |

## Como executar

### Pré-requisito

- Python 3.10 ou superior.

### Passos

```bash
git clone URL_DO_REPOSITORIO
cd AgendaSaude
python backend/app.py
```

Abra no navegador:

```text
http://127.0.0.1:8000
```

No Windows, também é possível dar duplo clique em `iniciar.bat`. Em Linux/macOS, use `./iniciar.sh`.

Não é necessário executar `pip install`, pois a prova de conceito usa somente bibliotecas nativas do Python.

### Usuário de demonstração

```text
E-mail: maria@agendasaude.demo
Senha: 123456
```

Também é possível criar um novo cadastro diretamente na tela inicial.

## Teste rápido da API

Com o backend em execução, abra outro terminal e rode:

```bash
python scripts/smoke_test.py
```

O teste verifica saúde da API, login, profissionais e consulta ao histórico.

## Estrutura do repositório

```text
AgendaSaude/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── backend/
│   └── app.py
├── database/
│   ├── README.md
│   ├── schema.sql
│   └── seed.sql
├── docs/
│   ├── primeira-etapa/
│   │   └── Projeto_Integrador_PARTE_1_2026.docx
│   ├── API.md
│   ├── ARQUITETURA.md
│   ├── ENTREGA_SEGUNDA_ETAPA.md
│   ├── Projeto_Integrador_SEGUNDA_ETAPA.docx
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── styles.css
├── scripts/
│   └── smoke_test.py
├── video/
│   └── README.md
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── requirements.txt
├── iniciar.bat
└── iniciar.sh
```

## Banco de dados

Na primeira execução, o backend cria automaticamente `database/agendasaude.db` usando:

- `database/schema.sql` para tabelas e índices;
- `database/seed.sql` para profissionais iniciais.

O arquivo `.db` é local e está no `.gitignore`; os scripts necessários para recriar a base ficam versionados no GitHub.

## API

A documentação dos endpoints está em [`docs/API.md`](docs/API.md).

## Integrantes

- ADRIANO VINICIUS LEITE DUTRA
- DANIELLE GUIMARAES ALBUQUERQUE
- KAILA MOTA SILVA
- LUCAS RIBEIRO DA SILVA MORAES
- MÔNICA FONTALVA SILVA
- SERGIO LOPES MORAES


A primeira entrega está preservada em `docs/primeira-etapa/`. A documentação da segunda etapa está em `docs/Projeto_Integrador_SEGUNDA_ETAPA.docx` e `docs/ENTREGA_SEGUNDA_ETAPA.md`.

## Observação

Este repositório é uma prova de conceito acadêmica. Para produção, seria necessário reforçar autenticação, autorização, proteção de dados pessoais, logs, testes automatizados, observabilidade, política de backup e implantação segura.
