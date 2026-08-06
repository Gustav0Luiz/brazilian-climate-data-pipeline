# Brazilian Climate Data Pipeline

Pipeline de dados para coleta, armazenamento, transformação, validação e visualização de informações climáticas das 27 capitais brasileiras.

O projeto coleta dados horários de temperatura e qualidade do ar por meio das APIs da Open-Meteo, armazena os dados no PostgreSQL, executa transformações com dbt, agenda todo o processo com Apache Airflow e disponibiliza um dashboard interativo em Streamlit.

## Arquitetura

```text
Open-Meteo APIs
        ↓
Python
        ↓
PostgreSQL — dados brutos
        ↓
Apache Airflow
        ↓
dbt — transformação e testes
        ↓
PostgreSQL — dados analíticos
        ↓
Streamlit Dashboard
```

## Tecnologias utilizadas

- Python
- PostgreSQL
- Apache Airflow
- dbt
- Docker e Docker Compose
- Streamlit
- Plotly
- SQLAlchemy

## Dados coletados

O projeto coleta dados horários para as 27 capitais brasileiras, incluindo:

- temperatura;
- PM2.5 e PM10;
- monóxido e dióxido de carbono;
- dióxido de nitrogênio;
- dióxido de enxofre;
- ozônio;
- metano;
- poeira e profundidade óptica de aerossóis;
- índice UV;
- AQI norte-americano;
- índice europeu de qualidade do ar.

## Tabelas do banco

### Dados brutos

```text
public.raw_temperature
public.raw_air_quality
```

### Dados transformados pelo dbt

```text
analytics.climate_hourly
analytics.climate_daily
analytics.climate_monthly
```

As tabelas analíticas possuem dados agregados por hora, dia e mês.

O dbt também executa testes para verificar:

- valores obrigatórios nulos;
- registros duplicados;
- dias sem 24 horas;
- valores negativos inválidos;
- alinhamento entre temperatura e qualidade do ar.

O dicionário completo das tabelas e colunas está disponível em:

```text
dicionario.md
```

## Pré-requisitos

Antes de executar o projeto, instale:

- Git;
- Docker;
- Docker Compose.

No Windows, recomenda-se utilizar Docker Desktop com WSL 2.

Não é necessário instalar localmente PostgreSQL, Airflow, dbt, Streamlit ou as bibliotecas Python do projeto.

## Como executar

Os comandos abaixo devem ser executados em Linux, macOS, WSL ou Git Bash.

### 1. Clonar o repositório

```bash
git clone https://github.com/Gustav0Luiz/brazilian-climate-data-pipeline.git
cd climate-project
```

### 2. Criar o arquivo de variáveis de ambiente

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

O arquivo `.env` contém as configurações usadas pelos contêineres.

Ele não deve ser enviado ao GitHub.

### 3. Configurar as variáveis

Abra o arquivo `.env` e substitua os valores de exemplo:

```dotenv
AIRFLOW_UID=1000
AIRFLOW_PROJ_DIR=.
ENV_FILE_PATH=.env

POSTGRES_DB=climate_db
POSTGRES_USER=climate_user
POSTGRES_PASSWORD=replace_with_a_secure_password
POSTGRES_HOST=climate-postgres
POSTGRES_PORT=5432

FERNET_KEY=replace_with_a_generated_fernet_key

AIRFLOW__API_AUTH__JWT_SECRET=replace_with_a_random_secret
AIRFLOW__API_AUTH__JWT_ISSUER=airflow

_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=replace_with_a_secure_password

_PIP_ADDITIONAL_REQUIREMENTS=
```

Em Linux ou WSL, descubra seu identificador de usuário com:

```bash
id -u
```

Use o resultado em:

```dotenv
AIRFLOW_UID=RESULTADO_DO_COMANDO
```

Mantenha:

```dotenv
POSTGRES_HOST=climate-postgres
```

Esse é o nome do serviço PostgreSQL dentro da rede do Docker.

### 4. Gerar a chave Fernet

Execute:

```bash
docker run --rm apache/airflow:3.3.0 \
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copie o resultado para:

```dotenv
FERNET_KEY=CHAVE_GERADA
```

### 5. Gerar o segredo JWT

Execute:

```bash
docker run --rm apache/airflow:3.3.0 \
  python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copie o resultado para:

```dotenv
AIRFLOW__API_AUTH__JWT_SECRET=SEGREDO_GERADO
```

### 6. Construir e iniciar os contêineres

Execute:

```bash
docker compose up -d --build
```

Esse único comando:

1. cria os bancos PostgreSQL;
2. inicializa o banco de metadados do Airflow;
3. cria o usuário administrador do Airflow;
4. inicia Redis e os componentes do Airflow;
5. inicia o dashboard Streamlit;
6. ativa a DAG de ingestão;
7. coleta os períodos ausentes;
8. executa os modelos e testes do dbt.

### 7. Verificar os serviços

```bash
docker compose ps
```

Os serviços permanentes devem aparecer como `Up` ou `healthy`.

O serviço `airflow-init` deve aparecer como:

```text
Exited (0)
```

Esse estado é normal: o serviço executa a inicialização e termina com sucesso.

## Primeira carga

Na primeira execução, o banco climático estará vazio.

O Airflow iniciará automaticamente a DAG:

```text
climate_ingestion
```

O pipeline identificará os períodos ausentes e coletará os dados até o último dia completo disponível.

A primeira carga pode demorar alguns minutos, principalmente devido ao intervalo aplicado entre as requisições de qualidade do ar.

Acompanhe a execução com:

```bash
docker compose logs -f airflow-worker
```

O fluxo executado será:

```text
run_ingestion
      ↓
run_dbt
```

Após a ingestão, o dbt cria as três tabelas analíticas e executa os testes de qualidade.

## Acessar as aplicações

### Airflow

Abra:

```text
http://localhost:8080
```

Utilize as credenciais definidas no `.env`:

```dotenv
_AIRFLOW_WWW_USER_USERNAME
_AIRFLOW_WWW_USER_PASSWORD
```

A DAG principal é:

```text
climate_ingestion
```

Ela é executada diariamente às 12h no fuso `America/Sao_Paulo`.

### Dashboard

Abra:

```text
http://localhost:8501
```

O dashboard permite:

- selecionar uma capital;
- escolher o período;
- visualizar temperaturas mínimas, médias e máximas;
- analisar AQI e poluentes;
- comparar temperatura e qualidade do ar;
- consultar os dados diários;
- exportar os dados selecionados em CSV.

Caso a primeira carga ainda não tenha terminado, o dashboard exibirá uma mensagem solicitando que o usuário aguarde.

## Comandos úteis

### Ver o estado dos serviços

```bash
docker compose ps
```

### Ver os logs do Airflow

```bash
docker compose logs -f airflow-worker
```

```bash
docker compose logs -f airflow-scheduler
```

### Ver os logs do dashboard

```bash
docker compose logs -f dashboard
```

### Ver os logs do banco climático

```bash
docker compose logs -f climate-postgres
```

### Parar os serviços

```bash
docker compose down
```

Esse comando para os contêineres, mas mantém os dados armazenados nos volumes Docker.

### Iniciar novamente

```bash
docker compose up -d
```

Ao ser iniciado novamente, o pipeline verifica automaticamente se existem períodos ausentes.

### Reconstruir as imagens

Use depois de alterar arquivos de dependências ou Dockerfiles:

```bash
docker compose up -d --build
```

### Apagar todos os dados

```bash
docker compose down -v
```

Atenção: esse comando remove os volumes Docker e apaga:

- dados climáticos;
- tabelas analíticas;
- histórico e configurações do Airflow.

Na próxima inicialização, o projeto será executado como uma instalação nova.

## Estrutura principal

```text
climate-project/
├── api_client.py
├── pipeline.py
├── utils.py
├── requirements.txt
├── docker-compose.yaml
├── Dockerfile.airflow
├── Dockerfile.dashboard
├── .env.example
├── dicionario.md
│
├── dags/
│   └── climate_ingestion_dag.py
│
├── sql/
│   └── init.sql
│
├── climate_dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── models/
│   └── tests/
│
└── dashboard/
    ├── app.py
    └── requirements.txt
```

## Persistência

Os dados são armazenados em volumes Docker.

Por isso, executar:

```bash
docker compose down
```

não apaga o banco.

Ao iniciar novamente, o Airflow continua utilizando o histórico anterior e o pipeline coleta apenas os períodos que ainda estiverem ausentes.

## Atualização automática

O processo diário é:

```text
12h — America/Sao_Paulo
        ↓
Airflow executa a ingestão
        ↓
Python coleta os dados do último dia completo
        ↓
PostgreSQL atualiza as tabelas brutas
        ↓
dbt atualiza as tabelas analíticas
        ↓
dbt executa os testes
        ↓
Streamlit passa a consultar os dados atualizados
```

Caso o computador esteja desligado no horário agendado, o Airflow executará a tarefa pendente quando os contêineres forem iniciados novamente.

O pipeline também verifica diretamente o banco de dados e recupera períodos ausentes sem criar registros duplicados.
