import requests
import datetime as dt
from utils import (AIR_QUALITY_VARIABLES,BRAZILIAN_CAPITALS as capitals,get_project_yesterday)
import os
import psycopg
from dotenv import load_dotenv
import time

        

load_dotenv()


########### ------------------ coleta de dados de temperatura -------------------- #############

## URL para coletar todos os dados antigos de uma vez
HISTORICAL_URL = "https://archive-api.open-meteo.com/v1/archive"

## URL para dados novos e diarios
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

def url_builder(request_type:str, city: str, begin_date: str | None = None, end_date: str | None = None) -> str:

    capital_data = capitals.get(city)
    if capital_data is None:
        raise ValueError(f"Capital não encontrada: {city}")

    latitude = capital_data["latitude"]
    longitude = capital_data["longitude"]

    yesterday = get_project_yesterday().isoformat()

    if request_type == "historical":
        base_url = HISTORICAL_URL
        start_date = begin_date or "2026-01-01"
        final_date = end_date or yesterday

    elif request_type == "forecast":
        base_url = FORECAST_URL
        start_date = begin_date or yesterday
        final_date = end_date or yesterday

    else:
        raise ValueError(
            "Tipo inválido. Use 'historical' ou 'forecast'."
        )

    return f"{base_url}?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={final_date}&hourly=temperature_2m&timezone=auto"
        

        
def fetch_old_data(city: str, begin_date: str | None = None, end_date: str | None = None,) -> dict:
    url = url_builder(request_type="historical",city=city,begin_date=begin_date, end_date=end_date)
    response = requests.get(url,timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_daily_data(city:str) -> dict:
    url = url_builder(request_type="forecast",city=city)
    response = requests.get(url,timeout=30)
    response.raise_for_status()
    return response.json()


## conectar com o postgres
def get_db_connection():
    return psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )



def build_temperature_rows(city: str, data: dict) -> list[tuple]:
    ## Converte o JSON obtido pela API em uma estrutura pronta para ser inserida na tabela.

    times = data["hourly"]["time"]
    temperatures = data["hourly"]["temperature_2m"]

    ## Verifica se todo registro de horario possui temperatura associada
    if len(times) != len(temperatures):
        raise ValueError(
            f"Quantidade de horários e temperaturas diferente para {city}"
        )

    rows = []

    for timestamp, temperature in zip(times, temperatures):
        measured_at = dt.datetime.fromisoformat(timestamp)

        rows.append(
            (
                city,
                data["latitude"],
                data["longitude"],
                measured_at,
                data["timezone"],
                temperature,
            )
        )

    return rows


## Comando para inserir cada linha no banco de dados. O Psycopg monta corretamente os dados via template com %s
## Em caso de dados duplicados apenas atualiza com o novo valor (exclui o antigo e adiciona o novo)
INSERT_TEMPERATURE_SQL = """
    INSERT INTO raw_temperature (
        city,
        latitude,
        longitude,
        measured_at_local,
        timezone,
        temperature_c
    )
    VALUES (%s, %s, %s, %s, %s, %s)

    ON CONFLICT (city, measured_at_local)
    DO UPDATE SET
        latitude = EXCLUDED.latitude,
        longitude = EXCLUDED.longitude,
        timezone = EXCLUDED.timezone,
        temperature_c = EXCLUDED.temperature_c,
        collected_at = CURRENT_TIMESTAMP;
"""


# preenche a tabela do banco de dados com TODOS os dados historicos
def fill_historical_data():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            for city in capitals:
                try:
                    print(f"Coletando {city}...")
                    data = fetch_old_data(city)
                    rows = build_temperature_rows(city, data)

                    cursor.executemany(INSERT_TEMPERATURE_SQL,rows)
                    connection.commit()

                    print(f"{city}: {len(rows)} registros inseridos ou atualizados.")               

                except Exception as error:
                    connection.rollback()
                    print(f"Erro ao processar {city}: {error}")
    finally:
        connection.close()


def fill_daily_data():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            for city in capitals:
                try:
                    print(f"Coletando dados diários de {city}...")
                    data = fetch_daily_data(city)
                    rows = build_temperature_rows(city, data)

                    cursor.executemany(INSERT_TEMPERATURE_SQL,rows)
                    connection.commit()

                    print(f"{city}: {len(rows)} registros inseridos!")               

                except Exception as error:
                    connection.rollback()
                    print(f"Erro ao processar {city}: {error}")
    finally:
        connection.close()


def fill_missing_data(begin_date: str,end_date: str):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            for city in capitals:
                try:
                    print(f"Recuperando {city}: "f"{begin_date} ate {end_date}...")
                    data = fetch_old_data(city=city,begin_date=begin_date,end_date=end_date)
                    rows = build_temperature_rows(city, data)

                    cursor.executemany(INSERT_TEMPERATURE_SQL,rows)
                    connection.commit()

                    print( f"{city}: {len(rows)} registros processados.")
                    time.sleep(5)
                except Exception as error:
                    connection.rollback()
                    print(f"Erro ao processar {city}: {error}")
    finally:
        connection.close()



# retorna os intervalos de data ausentes no banco de dados
def get_missing_date_ranges(connection,) -> list[tuple[str, str]]:
    
    yesterday = get_project_yesterday().isoformat()
    expected_records_per_day = len(capitals) * 24

    query = """
        WITH expected_dates AS (
            SELECT generate_series(
                %s::date,
                %s::date,
                INTERVAL '1 day'
            )::date AS measurement_date
        ),

        daily_counts AS (
            SELECT
                measured_at_local::date AS measurement_date,
                COUNT(*) AS total_records
            FROM raw_temperature
            WHERE measured_at_local::date BETWEEN %s::date AND %s::date
            GROUP BY measured_at_local::date
        )

        SELECT expected_dates.measurement_date
        FROM expected_dates

        LEFT JOIN daily_counts
            ON expected_dates.measurement_date =
               daily_counts.measurement_date

        WHERE COALESCE(daily_counts.total_records, 0) < %s

        ORDER BY expected_dates.measurement_date;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                dt.date(2026, 1, 1),
                yesterday,
                dt.date(2026, 1, 1),
                yesterday,
                expected_records_per_day,
            ),
        )

        result = cursor.fetchall()

    missing_dates = [ row[0] for row in result ]

    if not missing_dates:
        return []

    missing_ranges = []
    range_start = missing_dates[0]
    previous_date = missing_dates[0]

    for current_date in missing_dates[1:]:
        expected_next_date = previous_date + dt.timedelta(days=1)

        if current_date == expected_next_date:
            previous_date = current_date
            continue

        missing_ranges.append(
            (
                range_start.isoformat(),
                previous_date.isoformat(),
            )
        )

        range_start = current_date
        previous_date = current_date

    missing_ranges.append(
        (
            range_start.isoformat(),
            previous_date.isoformat(),
        )
    )

    return missing_ranges

########### ------------------ coleta de dados de qualidade do ar -------------------- #############

AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
    

def air_quality_url_builder(request_type: str,city: str,begin_date: str | None = None,end_date: str | None = None) -> str:

    capital_data = capitals.get(city)
    if capital_data is None:
        raise ValueError(f"Capital nao encontrada: {city}")

    latitude = capital_data["latitude"]
    longitude = capital_data["longitude"]

    yesterday = get_project_yesterday().isoformat()
        
    if request_type == "historical":
        start_date = begin_date or "2026-01-01"
        final_date = end_date or yesterday

    elif request_type == "forecast":
        start_date = begin_date or yesterday
        final_date = end_date or yesterday

    else:
        raise ValueError("Tipo invalido. Use 'historical' ou 'forecast'.")
            
    hourly_variables = ",".join(AIR_QUALITY_VARIABLES)

    return (f"{AIR_QUALITY_URL}?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={final_date}&hourly={hourly_variables}&timezone=auto")
        

def fetch_old_air_quality_data(city: str,begin_date: str | None = None,end_date: str | None = None) -> dict:
    url = air_quality_url_builder(request_type="historical",city=city,begin_date=begin_date,end_date=end_date) 
    response = requests.get(url,timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_daily_air_quality_data(city: str) -> dict:
    url = air_quality_url_builder(request_type="forecast",city=city)
    response = requests.get( url,timeout=30)
    response.raise_for_status()
    return response.json()


def build_air_quality_rows(city: str,data: dict,) -> list[tuple]:
    """Converte o JSON da API em registros para raw_air_quality."""

    hourly_data = data["hourly"]
    times = hourly_data["time"]

    missing_variables = [variable for variable in AIR_QUALITY_VARIABLES if variable not in hourly_data ]
        
    if missing_variables:
        raise ValueError(
            f"Variaveis ausentes para {city}: "
            f"{', '.join(missing_variables)}"
        )

    # Confirma que todos os arrays possuem um valor para cada horario.
    for variable in AIR_QUALITY_VARIABLES:
        if len(hourly_data[variable]) != len(times):
            raise ValueError(f"Quantidade de horarios e valores de {variable} diferente para {city}")

    rows = []

    for index, timestamp in enumerate(times):
        measured_at = dt.datetime.fromisoformat(timestamp)

        rows.append(
            (
                city,
                data["latitude"],
                data["longitude"],
                data.get("elevation"),
                measured_at,
                data["timezone"],
                data.get("timezone_abbreviation"),
                data.get("utc_offset_seconds"),

                hourly_data["pm10"][index],
                hourly_data["pm2_5"][index],

                hourly_data["carbon_monoxide"][index],
                hourly_data["carbon_dioxide"][index],
                hourly_data["nitrogen_dioxide"][index],
                hourly_data["sulphur_dioxide"][index],
                hourly_data["ozone"][index],
                hourly_data["methane"][index],

                hourly_data["aerosol_optical_depth"][index],
                hourly_data["dust"][index],

                hourly_data["uv_index"][index],
                hourly_data["uv_index_clear_sky"][index],

                hourly_data["european_aqi"][index],
                hourly_data["european_aqi_pm2_5"][index],
                hourly_data["european_aqi_pm10"][index],
                hourly_data["european_aqi_nitrogen_dioxide"][index],
                hourly_data["european_aqi_ozone"][index],
                hourly_data["european_aqi_sulphur_dioxide"][index],
                    
                hourly_data["us_aqi"][index],
                hourly_data["us_aqi_pm2_5"][index],
                hourly_data["us_aqi_pm10"][index],
                hourly_data["us_aqi_nitrogen_dioxide"][index],
                hourly_data["us_aqi_ozone"][index],
                hourly_data["us_aqi_sulphur_dioxide"][index],
                hourly_data["us_aqi_carbon_monoxide"][index], 
            )
        )

    return rows


## Comando para inserir cada linha no banco de dados.
## O Psycopg substitui corretamente os valores nos placeholders %s.
## Em caso de conflito entre cidade e horario, atualiza o registro existente.
INSERT_AIR_QUALITY_SQL = """
    INSERT INTO raw_air_quality (
        city,
        latitude,
        longitude,
        elevation,
        measured_at_local,
        timezone,
        timezone_abbreviation,
        utc_offset_seconds,
        pm10,
        pm2_5,
        carbon_monoxide,
        carbon_dioxide,
        nitrogen_dioxide,
        sulphur_dioxide,
        ozone,
        methane,
        aerosol_optical_depth,
        dust,
        uv_index,
        uv_index_clear_sky,
        european_aqi,
        european_aqi_pm2_5,
        european_aqi_pm10,
        european_aqi_nitrogen_dioxide,
        european_aqi_ozone,
        european_aqi_sulphur_dioxide,
        aqi,
        aqi_pm2_5,
        aqi_pm10,
        aqi_nitrogen_dioxide,
        aqi_ozone,
        aqi_sulphur_dioxide,
        aqi_carbon_monoxide
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s,
        %s
    )

    ON CONFLICT (city, measured_at_local)
    DO UPDATE SET
        latitude = EXCLUDED.latitude,
        longitude = EXCLUDED.longitude,
        elevation = EXCLUDED.elevation,
        timezone = EXCLUDED.timezone,
        timezone_abbreviation = EXCLUDED.timezone_abbreviation,
        utc_offset_seconds = EXCLUDED.utc_offset_seconds,
        pm10 = EXCLUDED.pm10,
        pm2_5 = EXCLUDED.pm2_5,
        carbon_monoxide = EXCLUDED.carbon_monoxide,
        carbon_dioxide = EXCLUDED.carbon_dioxide,
        nitrogen_dioxide = EXCLUDED.nitrogen_dioxide,
        sulphur_dioxide = EXCLUDED.sulphur_dioxide,
        ozone = EXCLUDED.ozone,
        methane = EXCLUDED.methane,
        aerosol_optical_depth = EXCLUDED.aerosol_optical_depth,
        dust = EXCLUDED.dust,
        uv_index = EXCLUDED.uv_index,
        uv_index_clear_sky = EXCLUDED.uv_index_clear_sky,
        european_aqi = EXCLUDED.european_aqi,
        european_aqi_pm2_5 = EXCLUDED.european_aqi_pm2_5,
        european_aqi_pm10 = EXCLUDED.european_aqi_pm10,
        european_aqi_nitrogen_dioxide =
            EXCLUDED.european_aqi_nitrogen_dioxide,
        european_aqi_ozone = EXCLUDED.european_aqi_ozone,
        european_aqi_sulphur_dioxide =
            EXCLUDED.european_aqi_sulphur_dioxide,
        aqi = EXCLUDED.aqi,
        aqi_pm2_5 = EXCLUDED.aqi_pm2_5,
        aqi_pm10 = EXCLUDED.aqi_pm10,
        aqi_nitrogen_dioxide = EXCLUDED.aqi_nitrogen_dioxide,
        aqi_ozone = EXCLUDED.aqi_ozone,
        aqi_sulphur_dioxide = EXCLUDED.aqi_sulphur_dioxide,
        aqi_carbon_monoxide = EXCLUDED.aqi_carbon_monoxide,
        collected_at = CURRENT_TIMESTAMP;
"""


# Preenche a tabela com todos os dados históricos de qualidade do ar.
def fill_historical_air_quality_data():
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            for city in capitals:
                try:
                    print(
                        f"Coletando dados históricos de qualidade "
                        f"do ar de {city}..."
                    )

                    data = fetch_old_air_quality_data(city)
                    rows = build_air_quality_rows(city, data)

                    cursor.executemany(
                        INSERT_AIR_QUALITY_SQL,
                        rows,
                    )

                    connection.commit()

                    print(
                        f"{city}: {len(rows)} registros "
                        f"inseridos ou atualizados."
                    )
                    time.sleep(5)
                except Exception as error:
                    connection.rollback()
                    print(f"Erro ao processar {city}: {error}")

    finally:
        connection.close()


# Preenche a tabela com os dados de qualidade do ar de ontem.
def fill_daily_air_quality_data():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            for city in capitals:
                try:
                    print(f"Coletando dados diários de qualidade do ar de {city}...")

                    data = fetch_daily_air_quality_data(city)
                    rows = build_air_quality_rows(city, data)

                    cursor.executemany(INSERT_AIR_QUALITY_SQL,rows)
                    connection.commit()

                    print(f"{city}: {len(rows)} registros inseridos ou atualizados.")
                    time.sleep(5)
                except Exception as error:
                    connection.rollback()
                    print(f"Erro ao processar {city}: {error}")
    finally:
        connection.close()


def fill_missing_air_quality_data(begin_date: str, end_date: str):
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            for city in capitals:
                try:
                    print(f"Recuperando qualidade do ar de {city}: {begin_date} ate {end_date}...")

                    data = fetch_old_air_quality_data( city=city,begin_date=begin_date,end_date=end_date)
                    rows = build_air_quality_rows(city, data)
                    cursor.executemany( INSERT_AIR_QUALITY_SQL,rows)
                    connection.commit()

                    print(f"{city}: {len(rows)} registros processados.")
                    time.sleep(5) ### PARA EVITAR TOO MANY REQUESTS

                except Exception as error:
                    connection.rollback()
                    print(f"Erro ao processar {city}: {error}")
    finally:
        connection.close()


# Retorna os intervalos de datas ausentes na tabela raw_air_quality.
def get_missing_air_quality_date_ranges(connection,) -> list[tuple[str, str]]:

    yesterday = get_project_yesterday().isoformat()
    initial_date = dt.date(2026, 1, 1)

    expected_records_per_day = len(capitals) * 24

    query = """
        WITH expected_dates AS (
            SELECT generate_series(
                %s::date,
                %s::date,
                INTERVAL '1 day'
            )::date AS measurement_date
        ),

        daily_counts AS (
            SELECT
                measured_at_local::date AS measurement_date,
                COUNT(*) AS total_records
            FROM raw_air_quality
            WHERE measured_at_local::date
                BETWEEN %s::date AND %s::date
            GROUP BY measured_at_local::date
        )

        SELECT expected_dates.measurement_date
        FROM expected_dates

        LEFT JOIN daily_counts
            ON expected_dates.measurement_date =
               daily_counts.measurement_date

        WHERE COALESCE(daily_counts.total_records, 0) < %s

        ORDER BY expected_dates.measurement_date;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                initial_date,
                yesterday,
                initial_date,
                yesterday,
                expected_records_per_day,
            ),
        )

        result = cursor.fetchall()

    missing_dates = [
        row[0]
        for row in result
    ]

    if not missing_dates:
        return []

    missing_ranges = []

    range_start = missing_dates[0]
    previous_date = missing_dates[0]

    for current_date in missing_dates[1:]:
        expected_next_date = (
            previous_date + dt.timedelta(days=1)
        )

        if current_date == expected_next_date:
            previous_date = current_date
            continue

        missing_ranges.append(
            (
                range_start.isoformat(),
                previous_date.isoformat(),
            )
        )

        range_start = current_date
        previous_date = current_date

    missing_ranges.append(
        (
            range_start.isoformat(),
            previous_date.isoformat(),
        )
    )

    return missing_ranges

