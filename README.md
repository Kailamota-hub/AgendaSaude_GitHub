# AgendaSaúde

Prova de conceito desenvolvida para o **Projeto Integrador – Segunda Etapa** do curso de Tecnologia em Análise e Desenvolvimento de Sistemas / TSI do SENAC.

O projeto dá continuidade à primeira entrega, na qual foram definidos a visão do produto, o problema, o público-alvo, os stakeholders, as personas e a jornada do usuário. Nesta etapa, a jornada da paciente **Maria Aparecida Santos** foi transformada em uma aplicação funcional.

---

## Objetivo do projeto

O **AgendaSaúde** tem como objetivo facilitar o gerenciamento e o agendamento de consultas em unidades de saúde, reduzindo filas, retrabalho, conflitos de horários e dificuldades de comunicação entre pacientes e profissionais.

A prova de conceito implementa o seguinte fluxo:

**Acesso → cadastro/login → escolha do profissional → escolha de data e horário → confirmação → acompanhamento → reagendamento/cancelamento**

---

## Funcionalidades implementadas

- Cadastro de usuários;
- Login e logout;
- Autenticação por token;
- Listagem de profissionais;
- Exibição de especialidades;
- Consulta de horários disponíveis;
- Agendamento de consultas;
- Prevenção de conflito de horários;
- Histórico de consultas;
- Reagendamento de consultas;
- Cancelamento de consultas;
- Persistência de dados em banco SQLite;
- Interface web integrada ao backend.

---

## Tecnologias utilizadas

### Frontend

- HTML5
- CSS3
- JavaScript

### Backend

- Python 3

### Banco de dados

- SQLite

### Comunicação

- API HTTP/REST
- JSON

### Versionamento

- Git
- GitHub

O backend principal foi desenvolvido utilizando bibliotecas nativas do Python.

---

## Estrutura do repositório

```text
AgendaSaude_GitHub/
│
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
│
├── backend/
│   └── app.py
│
├── database/
│   ├── README.md
│   ├── schema.sql
│   └── seed.sql
│
├── docs/
│   ├── primeira-etapa/
│   │   └── Projeto_Integrador_PARTE_1_2026.docx
│   ├── API.md
│   ├── ARQUITETURA.md
│   ├── ENTREGA_SEGUNDA_ETAPA.md
│   └── Projeto_Integrador_SEGUNDA_ETAPA.docx
│
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── styles.css
│
├── scripts/
│   └── smoke_test.py
│
├── tests/
│   ├── testes_automatizados/
│   │   ├── AgendarConsulta.py
│   │   ├── Login.py
│   │   └── ReagendarConsulta.py
│   ├── README.md
│   ├── __init__.py
│   ├── test_parse_positive_int.py
│   ├── test_password.py
│   ├── test_slots.py
│   └── test_validation.py
│
├── video/
│   └── video_PI_2026.mp4
│
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── iniciar.bat
├── iniciar.sh
└── requirements.txt
```

---

## Pré-requisitos

Para executar o projeto é necessário ter instalado:

- **Python 3.10 ou superior**
- **Git** (opcional, apenas para clonar o repositório)

Verifique a instalação do Python:

```bash
python --version
```

---

## Como clonar o projeto

Abra o terminal e execute:

```bash
git clone https://github.com/Kailamota-hub/AgendaSaude_GitHub.git
```

Depois entre na pasta:

```bash
cd AgendaSaude_GitHub
```

---

## Criando um ambiente virtual

É recomendado utilizar um ambiente virtual.

### Windows

```bash
python -m venv .venv
```

Ativação pelo Prompt de Comando:

```bash
.venv\Scripts\activate
```

Ativação pelo PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## Instalando os requisitos

Com o ambiente virtual ativado:

```bash
python -m pip install -r requirements.txt
```

O projeto principal utiliza somente bibliotecas nativas do Python, portanto é normal que não sejam instalados pacotes externos para a execução da aplicação principal.

---

## Executando o projeto

Na raiz do projeto, execute:

```bash
python backend/app.py
```

O terminal deverá exibir:

```text
AgendaSaúde disponível em http://127.0.0.1:8000
Para encerrar, pressione Ctrl+C.
```

Abra o navegador e acesse:

```text
http://127.0.0.1:8000
```

---

## Execução rápida no Windows

Também é possível iniciar o sistema com dois cliques no arquivo:

```text
iniciar.bat
```

Depois acesse:

```text
http://127.0.0.1:8000
```

---

## Usuário de demonstração

Para testar rapidamente o sistema:

**E-mail**

```text
maria@agendasaude.demo
```

**Senha**

```text
123456
```

Também é possível criar um novo cadastro diretamente pela aplicação.

---

## Fluxo recomendado para testes

Após iniciar o sistema:

1. Acessar a tela inicial;
2. Fazer login com o usuário de demonstração;
3. Visualizar os profissionais disponíveis;
4. Selecionar um profissional;
5. Escolher uma data;
6. Escolher um horário disponível;
7. Confirmar o agendamento;
8. Consultar o histórico;
9. Reagendar a consulta;
10. Cancelar a consulta;
11. Verificar a atualização do status.

---

## Banco de dados

O sistema utiliza **SQLite**.

Na primeira execução, o backend cria automaticamente o banco local utilizando:

```text
database/schema.sql
database/seed.sql
```

O arquivo `database/agendasaude.db` é criado localmente e não precisa ser versionado no GitHub.

O sistema também cria automaticamente o usuário de demonstração caso ele ainda não exista.

---

## API

Principais rotas utilizadas pelo sistema:

```text
GET    /api/health
GET    /api/me
GET    /api/doctors
GET    /api/slots
GET    /api/appointments

POST   /api/register
POST   /api/login
POST   /api/logout
POST   /api/appointments

PUT    /api/appointments/{id}

DELETE /api/appointments/{id}
```

A documentação detalhada está disponível em:

```text
docs/API.md
```

---

## Testes

### Teste rápido da API

Com o backend em execução, abra outro terminal e execute:

```bash
python scripts/smoke_test.py
```

### Testes unitários

Os testes unitários do backend podem ser executados com:

```bash
python -m unittest discover -s tests -v
```

Eles verificam regras como validação de dados, senhas e disponibilidade de horários.

### Testes automatizados de interface

A pasta:

```text
tests/testes_automatizados/
```

contém testes de interface para login, agendamento e reagendamento.

Esses scripts utilizam **Selenium** e abrem o Microsoft Edge para interagir com a aplicação. Para executá-los, o servidor do AgendaSaúde deve estar em funcionamento e o Selenium deve estar instalado no ambiente.

---

## Encerrando o servidor

No terminal onde o sistema está sendo executado, pressione:

```text
Ctrl + C
```

---

## Integrantes

- Adriano Vinicius Leite Dutra
- Danielle Guimaraes Albuquerque
- Kaila Mota Silva
- Mônica Fontalva Silva
- Sergio Lopes Moraes

---

## Vídeo de apresentação

O vídeo de apresentação está disponível em:

```text
video/video_PI_2026.mp4
```

O vídeo apresenta brevemente o funcionamento da prova de conceito.

---

## Documentação

A documentação complementar está disponível na pasta:

```text
docs/
```

Ela inclui:

- documentação da API;
- arquitetura da solução;
- documentação da primeira etapa;
- documentação da segunda etapa;
- relatório da segunda entrega em Word.

---

## Licença

Consulte o arquivo:

```text
LICENSE
```

para informações sobre a licença do projeto.

---

## Observação

Este repositório é uma prova de conceito acadêmica. Para produção, seria necessário reforçar autenticação, autorização, proteção de dados pessoais, logs, testes automatizados, observabilidade, política de backup e implantação segura.
