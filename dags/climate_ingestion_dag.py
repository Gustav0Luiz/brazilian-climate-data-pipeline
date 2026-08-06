from datetime import timedelta

import pendulum
from airflow.sdk import dag, task
from airflow.providers.standard.operators.bash import BashOperator


@dag(
    dag_id="climate_ingestion",
    description=(
        "Collects hourly temperature and air quality data "
        "for Brazilian capitals and builds analytics models."
    ),
    schedule="0 12 * * *",
    start_date=pendulum.datetime(
        2026,
        8,
        1,
        tz="America/Sao_Paulo",
    ),
    catchup=False,
    is_paused_upon_creation=False,
    max_active_runs=1,
    tags=["climate", "ingestion", "dbt"],
)
def climate_ingestion():

    @task(
        task_id="run_ingestion",
        retries=2,
        retry_delay=timedelta(minutes=5),
    )
    def execute_ingestion() -> None:
        from pipeline import run_ingestion

        run_ingestion()

    ingestion_task = execute_ingestion()

    dbt_task = BashOperator(
        task_id="run_dbt",
        bash_command=(
            "set -e; "
            "dbt build "
            "--project-dir /opt/airflow/climate_dbt "
            "--profiles-dir /opt/airflow/climate_dbt"
        ),
        cwd="/opt/airflow/climate_dbt",
        retries=1,
        retry_delay=timedelta(minutes=2),
    )

    ingestion_task >> dbt_task


climate_ingestion_dag = climate_ingestion()