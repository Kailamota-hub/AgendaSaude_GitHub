# Projeto Integrador - Segunda Etapa
## AgendaSaúde

### 1. Revisita do projeto e definição da prova de conceito

Na primeira etapa, o AgendaSaúde foi definido como uma aplicação híbrida para gerenciamento e agendamento de consultas em unidades básicas de saúde. O problema central identificado foi a dificuldade de organizar agendas, reduzir filas, evitar conflitos de horários e melhorar a comunicação com os pacientes.

Para a segunda etapa, a prova de conceito foi delimitada com base na jornada da persona **Maria Aparecida Santos**, paciente de 54 anos que busca uma solução simples, rápida e acessível pelo celular. A jornada selecionada contempla: **acesso ao sistema, cadastro/login, escolha de profissional e horário, confirmação, acompanhamento, cancelamento e reagendamento**.

A delimitação foi realizada para transformar a ideação da primeira etapa em uma solução funcional e demonstrável, preservando as necessidades mapeadas anteriormente e concentrando o desenvolvimento no fluxo principal de valor para o paciente.

### 2. Preparação do ambiente e tecnologias

Foram escolhidas tecnologias simples, gratuitas e adequadas a uma prova de conceito acadêmica:

- **Frontend:** HTML5, CSS3 e JavaScript;
- **Backend:** Python 3;
- **Banco de dados:** SQLite;
- **Versionamento:** Git e GitHub;
- **Comunicação:** API REST com JSON.

A escolha reduz dependências externas e permite executar todo o projeto com uma instalação padrão do Python 3.

### 3. Desenvolvimento do frontend

O frontend foi projetado de forma responsiva e contempla:

- tela de login e cadastro;
- credenciais de demonstração;
- seleção de profissional/especialidade;
- escolha de data;
- consulta de horários disponíveis;
- confirmação do agendamento;
- histórico de consultas;
- cancelamento;
- reagendamento;
- mensagens de confirmação e erro;
- indicadores de consultas agendadas e canceladas.

### 4. Desenvolvimento do backend e repositório de dados

O backend disponibiliza uma API REST responsável por:

- cadastro de pacientes;
- autenticação;
- consulta de profissionais;
- cálculo de horários livres;
- criação de consultas;
- consulta do histórico;
- cancelamento;
- reagendamento;
- validação de datas e horários;
- bloqueio de dupla reserva do mesmo horário.

O banco SQLite possui tabelas de usuários, profissionais e consultas. O arquivo `schema.sql` descreve a estrutura e o `seed.sql` inclui dados iniciais para demonstração.

### 5. Como executar

1. Instalar Python 3.10 ou superior.
2. Clonar ou baixar o repositório.
3. Abrir o terminal na pasta raiz.
4. Executar `python backend/app.py`.
5. Abrir `http://127.0.0.1:8000` no navegador.
6. Utilizar o acesso de demonstração: `maria@agendasaude.demo` / `123456`.

