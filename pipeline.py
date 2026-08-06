import datetime as dt
from utils import get_project_yesterday
from api_client import (fill_daily_air_quality_data,fill_daily_data,fill_missing_air_quality_data,fill_missing_data,get_db_connection,get_missing_air_quality_date_ranges,get_missing_date_ranges)
    


def run_temperature_ingestion() -> None:

    yesterday = dt.date.today() - dt.timedelta(days=1)
    yesterday_text = yesterday.isoformat()

    connection = get_db_connection()

    try:
        missing_ranges = get_missing_date_ranges(connection)
    finally:
        connection.close()

    if not missing_ranges:
        print("A tabela raw_temperature ja esta atualizada.")
        return

    print(f"Intervalos ausentes em raw_temperature: {missing_ranges}")

    for begin_date, end_date in missing_ranges:

        # execucao diaria normal: falta somente ontem.
        if (
            begin_date == yesterday_text
            and end_date == yesterday_text
        ):
            print(f"Coletando temperaturas de ontem: {yesterday_text}")
            fill_daily_data()

        # Primeira carga, atraso ou intervalo incompleto.
        else:
            print(f"Preenchendo temperaturas de {begin_date} ate {end_date}" )
            fill_missing_data(begin_date=begin_date,end_date=end_date)
                
    validate_temperature_ingestion()





def validate_temperature_ingestion() -> None:
    connection = get_db_connection()

    try:
        remaining_ranges = get_missing_date_ranges(connection)
    finally:
        connection.close()

    if remaining_ranges:
        raise RuntimeError(f"Ainda existem intervalos incompletos em raw_temperature:{remaining_ranges}" )
            

    print("Ingestao de temperatura concluida com sucesso.")



def run_air_quality_ingestion() -> None:

    yesterday = get_project_yesterday()
    yesterday_text = yesterday.isoformat()

    connection = get_db_connection()

    try:
        missing_ranges = (get_missing_air_quality_date_ranges(connection))
            
    finally:
        connection.close()

    if not missing_ranges:
        print("A tabela raw_air_quality ja esta atualizada.")
        return

    print( f"Intervalos ausentes em raw_air_quality: {missing_ranges}")

    for begin_date, end_date in missing_ranges:

        # Execucao diaria normal: falta somente ontem.
        if (
            begin_date == yesterday_text
            and end_date == yesterday_text
        ):
            print(f"Coletando qualidade do ar de ontem: {yesterday_text}")
            fill_daily_air_quality_data()

        # Primeira carga, atraso ou intervalo incompleto.
        else:
            print(f"Preenchendo qualidade do ar de {begin_date} ate {end_date}")
            fill_missing_air_quality_data(begin_date=begin_date,end_date=end_date)

    validate_air_quality_ingestion()



def validate_air_quality_ingestion() -> None:

    connection = get_db_connection()
    try:
        remaining_ranges = (get_missing_air_quality_date_ranges(connection))

    finally:
        connection.close()

    if remaining_ranges:
        raise RuntimeError(
            "Ainda existem intervalos incompletos em "
            f"raw_air_quality: {remaining_ranges}"
        )

    print("Ingestao de qualidade do ar concluida com sucesso.")
        
    


def run_ingestion() -> None:

    print("Iniciando ingestao de temperatura...")
    run_temperature_ingestion()

    print("Iniciando ingestao de qualidade do ar...")
    run_air_quality_ingestion()

    print("Pipeline completo executado com sucesso.")


if __name__ == "__main__":
    run_ingestion()