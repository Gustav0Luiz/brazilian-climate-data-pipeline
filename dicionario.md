# Dicionário de Dados — Climate Project

## `public.raw_temperature`

| Coluna | Tipo PostgreSQL | Aceita nulo? | Unidade/Formato | Descrição |
|---|---|:---:|---|---|
| `id` | `BIGINT` | Não | Inteiro | Identificador técnico. Chave primária; gerado automaticamente pela sequência `raw_temperature_id_seq`. |
| `city` | `VARCHAR(100)` | Não | Texto | Nome da capital. Compõe a restrição única com `measured_at_local`. |
| `latitude` | `NUMERIC(9,6)` | Não | Graus decimais | Latitude WGS84 do ponto ou célula de grade usado pela API. |
| `longitude` | `NUMERIC(9,6)` | Não | Graus decimais | Longitude WGS84 do ponto ou célula de grade usado pela API. |
| `measured_at_local` | `TIMESTAMP WITHOUT TIME ZONE` | Não | `YYYY-MM-DD HH:MM:SS` | Data e hora local da medição. Compõe a restrição única com `city`. |
| `timezone` | `VARCHAR(50)` | Não | Nome IANA | Fuso horário associado à capital, como `America/Sao_Paulo`. |
| `temperature_c` | `NUMERIC(5,2)` | Sim | °C | Temperatura do ar a 2 metros acima do solo. |
| `collected_at` | `TIMESTAMP WITH TIME ZONE` | Não | Timestamp com fuso | Momento da inserção ou atualização do registro. Padrão: `CURRENT_TIMESTAMP`. |

## `public.raw_air_quality`

| Coluna | Tipo PostgreSQL | Aceita nulo? | Unidade/Formato | Descrição |
|---|---|:---:|---|---|
| `id` | `BIGINT` | Não | Inteiro | Identificador técnico. Chave primária; gerado automaticamente pela sequência `raw_air_quality_id_seq`. |
| `city` | `VARCHAR(100)` | Não | Texto | Nome da capital. Compõe a restrição única com `measured_at_local`. |
| `latitude` | `NUMERIC(9,6)` | Não | Graus decimais | Latitude WGS84 da célula de grade usada pelo modelo de qualidade do ar. |
| `longitude` | `NUMERIC(9,6)` | Não | Graus decimais | Longitude WGS84 da célula de grade usada pelo modelo de qualidade do ar. |
| `elevation` | `NUMERIC(8,2)` | Sim | m | Elevação associada ao ponto retornado pela API. |
| `measured_at_local` | `TIMESTAMP WITHOUT TIME ZONE` | Não | `YYYY-MM-DD HH:MM:SS` | Data e hora local dos valores atmosféricos. Compõe a restrição única com `city`. |
| `timezone` | `VARCHAR(50)` | Não | Nome IANA | Fuso horário associado ao ponto. |
| `timezone_abbreviation` | `VARCHAR(20)` | Sim | Texto | Abreviação do fuso retornada pela API. |
| `utc_offset_seconds` | `INTEGER` | Sim | Segundos | Diferença entre o horário local e UTC. |
| `pm10` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração de partículas com diâmetro inferior a 10 µm. |
| `pm2_5` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração de partículas com diâmetro inferior a 2,5 µm. |
| `carbon_monoxide` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração de monóxido de carbono (CO). |
| `carbon_dioxide` | `NUMERIC(12,3)` | Sim | ppm | Concentração de dióxido de carbono (CO₂). |
| `nitrogen_dioxide` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração de dióxido de nitrogênio (NO₂). |
| `sulphur_dioxide` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração de dióxido de enxofre (SO₂). |
| `ozone` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração de ozônio (O₃). |
| `methane` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração de metano (CH₄). |
| `aerosol_optical_depth` | `NUMERIC(8,4)` | Sim | Adimensional | Profundidade óptica de aerossóis a 550 nm. |
| `dust` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração de partículas de poeira mineral próximas à superfície. |
| `uv_index` | `NUMERIC(6,2)` | Sim | Índice UV | Índice ultravioleta considerando a nebulosidade. |
| `uv_index_clear_sky` | `NUMERIC(6,2)` | Sim | Índice UV | Índice ultravioleta estimado para céu limpo. |
| `european_aqi` | `SMALLINT` | Sim | Índice | Índice europeu consolidado de qualidade do ar. |
| `european_aqi_pm2_5` | `SMALLINT` | Sim | Índice | Componente do índice europeu calculado a partir de PM2.5. |
| `european_aqi_pm10` | `SMALLINT` | Sim | Índice | Componente do índice europeu calculado a partir de PM10. |
| `european_aqi_nitrogen_dioxide` | `SMALLINT` | Sim | Índice | Componente do índice europeu calculado a partir de NO₂. |
| `european_aqi_ozone` | `SMALLINT` | Sim | Índice | Componente do índice europeu calculado a partir de O₃. |
| `european_aqi_sulphur_dioxide` | `SMALLINT` | Sim | Índice | Componente do índice europeu calculado a partir de SO₂. |
| `aqi` | `SMALLINT` | Sim | Índice | Índice norte-americano consolidado; corresponde a `us_aqi` na API. |
| `aqi_pm2_5` | `SMALLINT` | Sim | Índice | Componente do AQI norte-americano calculado a partir de PM2.5. |
| `aqi_pm10` | `SMALLINT` | Sim | Índice | Componente do AQI norte-americano calculado a partir de PM10. |
| `aqi_nitrogen_dioxide` | `SMALLINT` | Sim | Índice | Componente do AQI norte-americano calculado a partir de NO₂. |
| `aqi_ozone` | `SMALLINT` | Sim | Índice | Componente do AQI norte-americano calculado a partir de O₃. |
| `aqi_sulphur_dioxide` | `SMALLINT` | Sim | Índice | Componente do AQI norte-americano calculado a partir de SO₂. |
| `aqi_carbon_monoxide` | `SMALLINT` | Sim | Índice | Componente do AQI norte-americano calculado a partir de CO. |
| `collected_at` | `TIMESTAMP WITH TIME ZONE` | Não | Timestamp com fuso | Momento da inserção ou atualização do registro. Padrão: `CURRENT_TIMESTAMP`. |

## `analytics.climate_hourly`

| Coluna | Tipo PostgreSQL | Aceita nulo? | Unidade/Formato | Descrição |
|---|---|:---:|---|---|
| `city` | `VARCHAR(100)` | Sim | Texto | Capital brasileira. Chave lógica do modelo em conjunto com `measured_at_local`; validada por teste dbt. |
| `latitude` | `NUMERIC(9,6)` | Sim | Graus decimais | Latitude proveniente da tabela de temperatura. |
| `longitude` | `NUMERIC(9,6)` | Sim | Graus decimais | Longitude proveniente da tabela de temperatura. |
| `measured_at_local` | `TIMESTAMP WITHOUT TIME ZONE` | Sim | `YYYY-MM-DD HH:MM:SS` | Data e hora local da observação. Uma linha por cidade e hora. |
| `measurement_date` | `DATE` | Sim | `YYYY-MM-DD` | Data derivada de `measured_at_local`. |
| `measurement_hour` | `INTEGER` | Sim | 0–23 | Hora derivada de `measured_at_local`. |
| `timezone` | `VARCHAR(50)` | Sim | Nome IANA | Fuso horário associado à capital. |
| `temperature_c` | `NUMERIC(5,2)` | Sim | °C | Temperatura do ar a 2 metros acima do solo. |
| `elevation` | `NUMERIC(8,2)` | Sim | m | Elevação associada ao ponto de qualidade do ar. |
| `pm10` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração horária de PM10. |
| `pm2_5` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração horária de PM2.5. |
| `carbon_monoxide` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração horária de CO. |
| `carbon_dioxide` | `NUMERIC(12,3)` | Sim | ppm | Concentração horária de CO₂. |
| `nitrogen_dioxide` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração horária de NO₂. |
| `sulphur_dioxide` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração horária de SO₂. |
| `ozone` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração horária de O₃. |
| `methane` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração horária de CH₄. |
| `aerosol_optical_depth` | `NUMERIC(8,4)` | Sim | Adimensional | Profundidade óptica de aerossóis a 550 nm. |
| `dust` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração horária de poeira mineral. |
| `uv_index` | `NUMERIC(6,2)` | Sim | Índice UV | Índice UV horário considerando a nebulosidade. |
| `uv_index_clear_sky` | `NUMERIC(6,2)` | Sim | Índice UV | Índice UV horário estimado para céu limpo. |
| `european_aqi` | `SMALLINT` | Sim | Índice | Índice europeu consolidado. |
| `european_aqi_pm2_5` | `SMALLINT` | Sim | Índice | Componente europeu referente a PM2.5. |
| `european_aqi_pm10` | `SMALLINT` | Sim | Índice | Componente europeu referente a PM10. |
| `european_aqi_nitrogen_dioxide` | `SMALLINT` | Sim | Índice | Componente europeu referente a NO₂. |
| `european_aqi_ozone` | `SMALLINT` | Sim | Índice | Componente europeu referente a O₃. |
| `european_aqi_sulphur_dioxide` | `SMALLINT` | Sim | Índice | Componente europeu referente a SO₂. |
| `aqi` | `SMALLINT` | Sim | Índice | AQI norte-americano consolidado. |
| `aqi_pm2_5` | `SMALLINT` | Sim | Índice | Componente do AQI referente a PM2.5. |
| `aqi_pm10` | `SMALLINT` | Sim | Índice | Componente do AQI referente a PM10. |
| `aqi_nitrogen_dioxide` | `SMALLINT` | Sim | Índice | Componente do AQI referente a NO₂. |
| `aqi_ozone` | `SMALLINT` | Sim | Índice | Componente do AQI referente a O₃. |
| `aqi_sulphur_dioxide` | `SMALLINT` | Sim | Índice | Componente do AQI referente a SO₂. |
| `aqi_carbon_monoxide` | `SMALLINT` | Sim | Índice | Componente do AQI referente a CO. |
| `temperature_collected_at` | `TIMESTAMP WITH TIME ZONE` | Sim | Timestamp com fuso | Momento em que o registro de temperatura foi coletado ou atualizado. |
| `air_quality_collected_at` | `TIMESTAMP WITH TIME ZONE` | Sim | Timestamp com fuso | Momento em que o registro de qualidade do ar foi coletado ou atualizado. |

## `analytics.climate_daily`

| Coluna | Tipo PostgreSQL | Aceita nulo? | Unidade/Formato | Descrição |
|---|---|:---:|---|---|
| `city` | `VARCHAR(100)` | Sim | Texto | Capital brasileira. Chave lógica em conjunto com `measurement_date`; validada por teste dbt. |
| `measurement_date` | `DATE` | Sim | `YYYY-MM-DD` | Data da agregação. Uma linha por cidade e dia. |
| `temperature_avg` | `NUMERIC(5,2)` | Sim | °C | Temperatura média do dia. |
| `temperature_min` | `NUMERIC` | Sim | °C | Menor temperatura do dia. |
| `temperature_max` | `NUMERIC` | Sim | °C | Maior temperatura do dia. |
| `pm2_5_avg` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração média diária de PM2.5. |
| `pm2_5_max` | `NUMERIC` | Sim | µg/m³ | Maior concentração diária de PM2.5. |
| `pm10_avg` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração média diária de PM10. |
| `pm10_max` | `NUMERIC` | Sim | µg/m³ | Maior concentração diária de PM10. |
| `ozone_avg` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração média diária de ozônio. |
| `nitrogen_dioxide_avg` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração média diária de NO₂. |
| `sulphur_dioxide_avg` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração média diária de SO₂. |
| `carbon_monoxide_avg` | `NUMERIC(12,3)` | Sim | µg/m³ | Concentração média diária de CO. |
| `uv_index_max` | `NUMERIC` | Sim | Índice UV | Maior índice UV do dia. |
| `aqi_avg` | `NUMERIC(8,2)` | Sim | Índice | Média diária do AQI norte-americano. |
| `aqi_max` | `SMALLINT` | Sim | Índice | Maior AQI norte-americano do dia. |
| `european_aqi_avg` | `NUMERIC(8,2)` | Sim | Índice | Média diária do índice europeu. |
| `european_aqi_max` | `SMALLINT` | Sim | Índice | Maior índice europeu do dia. |
| `hourly_records` | `INTEGER` | Sim | Quantidade | Número de registros horários usados na agregação. O teste dbt exige 24 para cada cidade e dia. |

## `analytics.climate_monthly`

| Coluna | Tipo PostgreSQL | Aceita nulo? | Unidade/Formato | Descrição |
|---|---|:---:|---|---|
| `city` | `VARCHAR(100)` | Sim | Texto | Capital brasileira. Chave lógica em conjunto com `measurement_month`; validada por teste dbt. |
| `measurement_month` | `DATE` | Sim | `YYYY-MM-01` | Mês da agregação representado pelo primeiro dia do mês. Uma linha por cidade e mês. |
| `measurement_year` | `INTEGER` | Sim | Ano | Ano extraído de `measurement_month`. |
| `measurement_month_number` | `INTEGER` | Sim | 1–12 | Número do mês extraído de `measurement_month`. |
| `temperature_avg` | `NUMERIC` | Sim | °C | Temperatura média do mês. |
| `temperature_min` | `NUMERIC` | Sim | °C | Menor temperatura do mês. |
| `temperature_max` | `NUMERIC` | Sim | °C | Maior temperatura do mês. |
| `pm2_5_avg` | `NUMERIC` | Sim | µg/m³ | Concentração média mensal de PM2.5. |
| `pm2_5_max` | `NUMERIC` | Sim | µg/m³ | Maior concentração mensal de PM2.5. |
| `pm10_avg` | `NUMERIC` | Sim | µg/m³ | Concentração média mensal de PM10. |
| `pm10_max` | `NUMERIC` | Sim | µg/m³ | Maior concentração mensal de PM10. |
| `ozone_avg` | `NUMERIC` | Sim | µg/m³ | Concentração média mensal de ozônio. |
| `ozone_max` | `NUMERIC` | Sim | µg/m³ | Maior concentração mensal de ozônio. |
| `nitrogen_dioxide_avg` | `NUMERIC` | Sim | µg/m³ | Concentração média mensal de NO₂. |
| `sulphur_dioxide_avg` | `NUMERIC` | Sim | µg/m³ | Concentração média mensal de SO₂. |
| `carbon_monoxide_avg` | `NUMERIC` | Sim | µg/m³ | Concentração média mensal de CO. |
| `uv_index_max` | `NUMERIC` | Sim | Índice UV | Maior índice UV do mês. |
| `aqi_avg` | `NUMERIC` | Sim | Índice | Média mensal do AQI norte-americano. |
| `aqi_max` | `SMALLINT` | Sim | Índice | Maior AQI norte-americano do mês. |
| `european_aqi_avg` | `NUMERIC` | Sim | Índice | Média mensal do índice europeu. |
| `european_aqi_max` | `SMALLINT` | Sim | Índice | Maior índice europeu do mês. |
| `hourly_records` | `INTEGER` | Sim | Quantidade | Número de registros horários usados na agregação mensal. |
| `days_present` | `INTEGER` | Sim | Quantidade | Número de dias distintos presentes no mês para a cidade. |
