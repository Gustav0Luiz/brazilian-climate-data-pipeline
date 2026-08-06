import datetime as dt
import os

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine import Engine


st.set_page_config(
    page_title="Brazilian Climate Dashboard",
    page_icon="🌤️",
    layout="wide",
)


@st.cache_resource
def get_database_engine() -> Engine:
    """Cria e reutiliza o pool de conexões com o PostgreSQL."""

    required_variables = [
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ]

    missing_variables = [
        variable
        for variable in required_variables
        if not os.getenv(variable)
    ]

    if missing_variables:
        raise RuntimeError(
            "Variáveis de ambiente ausentes: "
            + ", ".join(missing_variables)
        )

    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        database=os.environ["POSTGRES_DB"],
    )

    return create_engine(
        database_url,
        pool_pre_ping=True,
    )

@st.cache_data(ttl=30)
def analytics_is_ready() -> bool:
    """Verifica se a tabela analitica existe e possui dados."""

    table_query = text(
        """
        SELECT to_regclass(
            'analytics.climate_daily'
        ) AS table_name
        """
    )

    with get_database_engine().connect() as connection:
        table_result = pd.read_sql(
            table_query,
            connection,
        )

    if table_result.loc[0, "table_name"] is None:
        return False

    data_query = text(
        """
        SELECT EXISTS (
            SELECT 1
            FROM analytics.climate_daily
        ) AS has_data
        """
    )

    with get_database_engine().connect() as connection:
        data_result = pd.read_sql(
            data_query,
            connection,
        )

    return bool(data_result.loc[0, "has_data"])



@st.cache_data(ttl=300)
def load_cities() -> list[str]:
    """Retorna as capitais disponíveis na tabela diária."""

    query = text(
        """
        SELECT DISTINCT city
        FROM analytics.climate_daily
        ORDER BY city
        """
    )

    with get_database_engine().connect() as connection:
        dataframe = pd.read_sql(query, connection)

    return dataframe["city"].tolist()


@st.cache_data(ttl=300)
def load_date_bounds() -> tuple[dt.date, dt.date]:
    """Retorna a menor e a maior data disponíveis."""

    query = text(
        """
        SELECT
            MIN(measurement_date) AS minimum_date,
            MAX(measurement_date) AS maximum_date
        FROM analytics.climate_daily
        """
    )

    with get_database_engine().connect() as connection:
        dataframe = pd.read_sql(query, connection)

    minimum_date = dataframe.loc[0, "minimum_date"]
    maximum_date = dataframe.loc[0, "maximum_date"]

    if minimum_date is None or maximum_date is None:
        raise RuntimeError(
            "A tabela analytics.climate_daily não possui dados."
        )

    return (
        pd.to_datetime(minimum_date).date(),
        pd.to_datetime(maximum_date).date(),
    )


@st.cache_data(ttl=300)
def load_daily_data(
    city: str,
    start_date: dt.date,
    end_date: dt.date,
) -> pd.DataFrame:
    """Carrega os dados diários da capital e período selecionados."""

    query = text(
        """
        SELECT
            city,
            measurement_date,
            temperature_avg,
            temperature_min,
            temperature_max,
            pm2_5_avg,
            pm2_5_max,
            pm10_avg,
            pm10_max,
            ozone_avg,
            nitrogen_dioxide_avg,
            sulphur_dioxide_avg,
            carbon_monoxide_avg,
            uv_index_max,
            aqi_avg,
            aqi_max,
            european_aqi_avg,
            european_aqi_max,
            hourly_records
        FROM analytics.climate_daily
        WHERE city = :city
          AND measurement_date BETWEEN :start_date AND :end_date
        ORDER BY measurement_date
        """
    )

    parameters = {
        "city": city,
        "start_date": start_date,
        "end_date": end_date,
    }

    with get_database_engine().connect() as connection:
        dataframe = pd.read_sql(
            query,
            connection,
            params=parameters,
        )

    if not dataframe.empty:
        dataframe["measurement_date"] = pd.to_datetime(
            dataframe["measurement_date"]
        )

    return dataframe


def format_number(
    value: float,
    decimal_places: int = 1,
) -> str:
    """Formata valores numéricos para exibição."""

    if pd.isna(value):
        return "—"

    return f"{value:.{decimal_places}f}"


def classify_aqi(value: float) -> str:
    """Classificação geral do AQI norte-americano."""

    if pd.isna(value):
        return "Sem dados"

    if value <= 50:
        return "Boa"

    if value <= 100:
        return "Moderada"

    if value <= 150:
        return "Insalubre para grupos sensíveis"

    if value <= 200:
        return "Insalubre"

    if value <= 300:
        return "Muito insalubre"

    return "Perigosa"


# -------------------------------------------------------------------
# Cabeçalho
# -------------------------------------------------------------------

st.title("🌤️ Brazilian Climate Dashboard")

st.write(
    "Visualização interativa de temperatura e qualidade do ar "
    "das capitais brasileiras."
)

st.caption(
    "Dados coletados da Open-Meteo, processados com Airflow e dbt."
)


# -------------------------------------------------------------------
# Carregamento inicial
# -------------------------------------------------------------------

try:
    if not analytics_is_ready():
        st.info(
            "O pipeline ainda esta realizando a primeira carga. "
            "Aguarde alguns minutos e atualize esta pagina."
        )
        st.stop()

    cities = load_cities()
    minimum_date, maximum_date = load_date_bounds()

except Exception as error:
    st.error(
        "Não foi possível carregar os dados do PostgreSQL."
    )
    st.code(str(error))
    st.stop()


if not cities:
    st.warning("Nenhuma capital foi encontrada no banco de dados.")
    st.stop()


# -------------------------------------------------------------------
# Filtros
# -------------------------------------------------------------------

with st.sidebar:
    st.header("Filtros")

    selected_city = st.selectbox(
        label="Capital",
        options=cities,
    )

    default_start_date = max(
        minimum_date,
        maximum_date - dt.timedelta(days=29),
    )

    selected_period = st.date_input(
        label="Período",
        value=(default_start_date, maximum_date),
        min_value=minimum_date,
        max_value=maximum_date,
        format="DD/MM/YYYY",
    )

    refresh_button = st.button(
        label="Atualizar dados",
        width="stretch",
    )

    if refresh_button:
        st.cache_data.clear()
        st.rerun()

    st.divider()

    st.write(
        f"**Primeira data:** "
        f"{minimum_date.strftime('%d/%m/%Y')}"
    )

    st.write(
        f"**Última data:** "
        f"{maximum_date.strftime('%d/%m/%Y')}"
    )


if (
    not isinstance(selected_period, (tuple, list))
    or len(selected_period) != 2
):
    st.info("Selecione uma data inicial e uma data final.")
    st.stop()


start_date, end_date = selected_period


if start_date > end_date:
    st.error("A data inicial não pode ser posterior à data final.")
    st.stop()


# -------------------------------------------------------------------
# Consulta
# -------------------------------------------------------------------

try:
    daily_data = load_daily_data(
        city=selected_city,
        start_date=start_date,
        end_date=end_date,
    )

except Exception as error:
    st.error("Não foi possível consultar os dados selecionados.")
    st.code(str(error))
    st.stop()


if daily_data.empty:
    st.warning("Não existem dados para o período selecionado.")
    st.stop()


# -------------------------------------------------------------------
# Métricas
# -------------------------------------------------------------------

st.subheader(selected_city)

st.caption(
    f"Período selecionado: "
    f"{start_date.strftime('%d/%m/%Y')} a "
    f"{end_date.strftime('%d/%m/%Y')}"
)

average_temperature = daily_data["temperature_avg"].mean()
minimum_temperature = daily_data["temperature_min"].min()
maximum_temperature = daily_data["temperature_max"].max()
average_aqi = daily_data["aqi_avg"].mean()
average_pm2_5 = daily_data["pm2_5_avg"].mean()
maximum_uv = daily_data["uv_index_max"].max()


metric_1, metric_2, metric_3 = st.columns(3)

metric_1.metric(
    label="Temperatura média",
    value=f"{format_number(average_temperature)} °C",
)

metric_2.metric(
    label="Menor temperatura",
    value=f"{format_number(minimum_temperature)} °C",
)

metric_3.metric(
    label="Maior temperatura",
    value=f"{format_number(maximum_temperature)} °C",
)


metric_4, metric_5, metric_6 = st.columns(3)

metric_4.metric(
    label="AQI médio",
    value=format_number(average_aqi),
    help=classify_aqi(average_aqi),
)

metric_5.metric(
    label="PM2.5 médio",
    value=f"{format_number(average_pm2_5)} µg/m³",
)

metric_6.metric(
    label="Índice UV máximo",
    value=format_number(maximum_uv),
)


# -------------------------------------------------------------------
# Abas
# -------------------------------------------------------------------

temperature_tab, air_tab, relationship_tab, data_tab = st.tabs(
    [
        "Temperatura",
        "Qualidade do ar",
        "Relação entre variáveis",
        "Dados",
    ]
)


# -------------------------------------------------------------------
# Temperatura
# -------------------------------------------------------------------

with temperature_tab:
    st.subheader("Evolução diária da temperatura")

    temperature_chart_data = daily_data[
        [
            "measurement_date",
            "temperature_min",
            "temperature_avg",
            "temperature_max",
        ]
    ].melt(
        id_vars=["measurement_date"],
        var_name="measurement",
        value_name="temperature_c",
    )

    temperature_chart_data["measurement"] = (
        temperature_chart_data["measurement"].replace(
            {
                "temperature_min": "Mínima",
                "temperature_avg": "Média",
                "temperature_max": "Máxima",
            }
        )
    )

    temperature_figure = px.line(
        temperature_chart_data,
        x="measurement_date",
        y="temperature_c",
        color="measurement",
        markers=True,
        labels={
            "measurement_date": "Data",
            "temperature_c": "Temperatura (°C)",
            "measurement": "Medição",
        },
    )

    temperature_figure.update_layout(
        legend_title_text="Temperatura",
        hovermode="x unified",
    )

    temperature_figure.update_xaxes(
        tickformat="%d/%m/%Y",
    )

    st.plotly_chart(
        temperature_figure,
        width="stretch",
    )


# -------------------------------------------------------------------
# Qualidade do ar
# -------------------------------------------------------------------

with air_tab:
    st.subheader("Índice de qualidade do ar")

    aqi_chart_data = daily_data[
        [
            "measurement_date",
            "aqi_avg",
            "aqi_max",
            "european_aqi_avg",
            "european_aqi_max",
        ]
    ].melt(
        id_vars=["measurement_date"],
        var_name="measurement",
        value_name="aqi_value",
    )

    aqi_chart_data["measurement"] = (
        aqi_chart_data["measurement"].replace(
            {
                "aqi_avg": "AQI médio",
                "aqi_max": "AQI máximo",
                "european_aqi_avg": "AQI europeu médio",
                "european_aqi_max": "AQI europeu máximo",
            }
        )
    )

    aqi_figure = px.line(
        aqi_chart_data,
        x="measurement_date",
        y="aqi_value",
        color="measurement",
        labels={
            "measurement_date": "Data",
            "aqi_value": "Índice",
            "measurement": "Medição",
        },
    )

    aqi_figure.update_layout(
        legend_title_text="Índice",
        hovermode="x unified",
    )

    aqi_figure.update_xaxes(
        tickformat="%d/%m/%Y",
    )

    st.plotly_chart(
        aqi_figure,
        width="stretch",
    )

    st.subheader("Material particulado")

    particles_chart_data = daily_data[
        [
            "measurement_date",
            "pm2_5_avg",
            "pm10_avg",
        ]
    ].melt(
        id_vars=["measurement_date"],
        var_name="pollutant",
        value_name="concentration",
    )

    particles_chart_data["pollutant"] = (
        particles_chart_data["pollutant"].replace(
            {
                "pm2_5_avg": "PM2.5",
                "pm10_avg": "PM10",
            }
        )
    )

    particles_figure = px.line(
        particles_chart_data,
        x="measurement_date",
        y="concentration",
        color="pollutant",
        labels={
            "measurement_date": "Data",
            "concentration": "Concentração (µg/m³)",
            "pollutant": "Poluente",
        },
    )

    particles_figure.update_layout(
        legend_title_text="Poluente",
        hovermode="x unified",
    )

    particles_figure.update_xaxes(
        tickformat="%d/%m/%Y",
    )

    st.plotly_chart(
        particles_figure,
        width="stretch",
    )

    st.subheader("Outros poluentes")

    pollutants_chart_data = daily_data[
        [
            "measurement_date",
            "ozone_avg",
            "nitrogen_dioxide_avg",
            "sulphur_dioxide_avg",
            "carbon_monoxide_avg",
        ]
    ].melt(
        id_vars=["measurement_date"],
        var_name="pollutant",
        value_name="concentration",
    )

    pollutants_chart_data["pollutant"] = (
        pollutants_chart_data["pollutant"].replace(
            {
                "ozone_avg": "Ozônio",
                "nitrogen_dioxide_avg": "Dióxido de nitrogênio",
                "sulphur_dioxide_avg": "Dióxido de enxofre",
                "carbon_monoxide_avg": "Monóxido de carbono",
            }
        )
    )

    pollutants_figure = px.line(
        pollutants_chart_data,
        x="measurement_date",
        y="concentration",
        color="pollutant",
        labels={
            "measurement_date": "Data",
            "concentration": "Concentração (µg/m³)",
            "pollutant": "Poluente",
        },
    )

    pollutants_figure.update_layout(
        legend_title_text="Poluente",
        hovermode="x unified",
    )

    pollutants_figure.update_xaxes(
        tickformat="%d/%m/%Y",
    )

    st.plotly_chart(
        pollutants_figure,
        width="stretch",
    )


# -------------------------------------------------------------------
# Relações entre variáveis
# -------------------------------------------------------------------

with relationship_tab:
    st.subheader("Temperatura média × AQI médio")

    relationship_figure = px.scatter(
        daily_data,
        x="temperature_avg",
        y="aqi_avg",
        color="pm2_5_avg",
        size="pm10_avg",
        hover_data={
            "measurement_date": "|%d/%m/%Y",
            "temperature_avg": ":.2f",
            "aqi_avg": ":.2f",
            "pm2_5_avg": ":.3f",
            "pm10_avg": ":.3f",
        },
        labels={
            "temperature_avg": "Temperatura média (°C)",
            "aqi_avg": "AQI médio",
            "pm2_5_avg": "PM2.5 médio",
            "pm10_avg": "PM10 médio",
        },
    )

    st.plotly_chart(
        relationship_figure,
        width="stretch",
    )


# -------------------------------------------------------------------
# Tabela
# -------------------------------------------------------------------

with data_tab:
    st.subheader("Dados diários")

    displayed_columns = [
        "measurement_date",
        "temperature_avg",
        "temperature_min",
        "temperature_max",
        "pm2_5_avg",
        "pm2_5_max",
        "pm10_avg",
        "pm10_max",
        "ozone_avg",
        "nitrogen_dioxide_avg",
        "sulphur_dioxide_avg",
        "carbon_monoxide_avg",
        "uv_index_max",
        "aqi_avg",
        "aqi_max",
        "european_aqi_avg",
        "european_aqi_max",
        "hourly_records",
    ]

    st.dataframe(
        daily_data[displayed_columns],
        width="stretch",
        hide_index=True,
        column_config={
            "measurement_date": st.column_config.DateColumn(
                "Data",
                format="DD/MM/YYYY",
            ),
            "temperature_avg": st.column_config.NumberColumn(
                "Temperatura média",
                format="%.2f °C",
            ),
            "temperature_min": st.column_config.NumberColumn(
                "Temperatura mínima",
                format="%.2f °C",
            ),
            "temperature_max": st.column_config.NumberColumn(
                "Temperatura máxima",
                format="%.2f °C",
            ),
            "pm2_5_avg": st.column_config.NumberColumn(
                "PM2.5 médio",
                format="%.3f",
            ),
            "pm2_5_max": st.column_config.NumberColumn(
                "PM2.5 máximo",
                format="%.3f",
            ),
            "pm10_avg": st.column_config.NumberColumn(
                "PM10 médio",
                format="%.3f",
            ),
            "pm10_max": st.column_config.NumberColumn(
                "PM10 máximo",
                format="%.3f",
            ),
            "ozone_avg": st.column_config.NumberColumn(
                "Ozônio médio",
                format="%.3f",
            ),
            "nitrogen_dioxide_avg": st.column_config.NumberColumn(
                "NO₂ médio",
                format="%.3f",
            ),
            "sulphur_dioxide_avg": st.column_config.NumberColumn(
                "SO₂ médio",
                format="%.3f",
            ),
            "carbon_monoxide_avg": st.column_config.NumberColumn(
                "CO médio",
                format="%.3f",
            ),
            "uv_index_max": st.column_config.NumberColumn(
                "UV máximo",
                format="%.2f",
            ),
            "aqi_avg": st.column_config.NumberColumn(
                "AQI médio",
                format="%.2f",
            ),
            "aqi_max": st.column_config.NumberColumn(
                "AQI máximo",
                format="%d",
            ),
            "european_aqi_avg": st.column_config.NumberColumn(
                "AQI europeu médio",
                format="%.2f",
            ),
            "european_aqi_max": st.column_config.NumberColumn(
                "AQI europeu máximo",
                format="%d",
            ),
            "hourly_records": st.column_config.NumberColumn(
                "Horas coletadas",
                format="%d",
            ),
        },
    )

    csv_data = daily_data[displayed_columns].to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Baixar dados em CSV",
        data=csv_data,
        file_name=(
            f"climate_{selected_city.lower().replace(' ', '_')}_"
            f"{start_date}_{end_date}.csv"
        ),
        mime="text/csv",
    )