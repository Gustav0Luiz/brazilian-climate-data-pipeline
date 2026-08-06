# Climate dbt Project

Projeto dbt responsável por transformar os dados climáticos brutos armazenados no PostgreSQL em tabelas analíticas utilizadas pelo dashboard.

## Fluxo de transformação

```text
public.raw_temperature
public.raw_air_quality
          ↓
analytics.climate_hourly
          ↓
analytics.climate_daily
analytics.climate_monthly
```

## Modelos

### `climate_hourly`

Combina os dados horários de temperatura e qualidade do ar utilizando a cidade e o horário da medição.

Materialização:

```text
table
```

### `climate_daily`

Agrega os dados por cidade e dia, calculando indicadores como:

- temperatura média, mínima e máxima;
- médias e máximas de PM2.5 e PM10;
- médias de poluentes;
- índice UV máximo;
- AQI médio e máximo;
- quantidade de registros horários.

Materialização:

```text
table
```

### `climate_monthly`

Agrega os dados por cidade e mês, produzindo indicadores mensais de temperatura, poluentes, qualidade do ar e cobertura dos dados.

Materialização:

```text
table
```

## Testes de qualidade

O projeto possui testes para verificar:

- registros duplicados;
- valores negativos inválidos;
- presença de 24 registros horários por dia;
- alinhamento entre as tabelas brutas de temperatura e qualidade do ar;
- preenchimento e unicidade das colunas principais.

Os testes são executados juntamente com os modelos por meio do comando:

```bash
dbt build
```

## Execução pelo Airflow

A DAG `climate_ingestion` executa primeiro a ingestão dos dados e, em seguida, o processo de transformação e validação do dbt:

```text
run_ingestion
      ↓
run_dbt
```

## Execução manual

Na raiz do repositório, com os contêineres em execução, utilize:

```bash
docker compose exec airflow-scheduler \
  dbt build \
  --project-dir /opt/airflow/climate_dbt \
  --profiles-dir /opt/airflow/climate_dbt
```

## Estrutura

```text
climate_dbt/
├── dbt_project.yml
├── profiles.yml
├── models/
│   ├── sources.yml
│   ├── schema.yml
│   ├── climate_hourly.sql
│   ├── climate_daily.sql
│   └── climate_monthly.sql
└── tests/
```

## Documentação relacionada

- [Documentação principal do projeto](../README.md)
- [Dicionário de dados](../dicionario.md)
