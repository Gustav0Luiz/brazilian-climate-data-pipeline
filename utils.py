import datetime as dt
from zoneinfo import ZoneInfo


PROJECT_TIMEZONE = ZoneInfo("America/Sao_Paulo")


def get_project_today() -> dt.date:
    return dt.datetime.now(PROJECT_TIMEZONE).date()


def get_project_yesterday() -> dt.date:
    return get_project_today() - dt.timedelta(days=1)


BRAZILIAN_CAPITALS = {
    "Rio Branco": {
        "state": "Acre",
        "state_code": "AC",
        "latitude": -9.97499,
        "longitude": -67.82430,
    },
    "Maceio": {
        "state": "Alagoas",
        "state_code": "AL",
        "latitude": -9.66599,
        "longitude": -35.73500,
    },
    "Macapa": {
        "state": "Amapa",
        "state_code": "AP",
        "latitude": 0.03493,
        "longitude": -51.06940,
    },
    "Manaus": {
        "state": "Amazonas",
        "state_code": "AM",
        "latitude": -3.11903,
        "longitude": -60.02170,
    },
    "Salvador": {
        "state": "Bahia",
        "state_code": "BA",
        "latitude": -12.97140,
        "longitude": -38.50140,
    },
    "Fortaleza": {
        "state": "Ceara",
        "state_code": "CE",
        "latitude": -3.73186,
        "longitude": -38.52670,
    },
    "Brasilia": {
        "state": "Distrito Federal",
        "state_code": "DF",
        "latitude": -15.79389,
        "longitude": -47.88278,
    },
    "Vitoria": {
        "state": "Espirito Santo",
        "state_code": "ES",
        "latitude": -20.31550,
        "longitude": -40.31280,
    },
    "Goiania": {
        "state": "Goias",
        "state_code": "GO",
        "latitude": -16.68690,
        "longitude": -49.26480,
    },
    "Sao Luis": {
        "state": "Maranhao",
        "state_code": "MA",
        "latitude": -2.53073,
        "longitude": -44.30680,
    },
    "Cuiaba": {
        "state": "Mato Grosso",
        "state_code": "MT",
        "latitude": -15.60140,
        "longitude": -56.09790,
    },
    "Campo Grande": {
        "state": "Mato Grosso do Sul",
        "state_code": "MS",
        "latitude": -20.46970,
        "longitude": -54.62010,
    },
    "Belo Horizonte": {
        "state": "Minas Gerais",
        "state_code": "MG",
        "latitude": -19.91670,
        "longitude": -43.93450,
    },
    "Belem": {
        "state": "Para",
        "state_code": "PA",
        "latitude": -1.45583,
        "longitude": -48.49020,
    },
    "Joao Pessoa": {
        "state": "Paraiba",
        "state_code": "PB",
        "latitude": -7.11950,
        "longitude": -34.84500,
    },
    "Curitiba": {
        "state": "Parana",
        "state_code": "PR",
        "latitude": -25.42840,
        "longitude": -49.27330,
    },
    "Recife": {
        "state": "Pernambuco",
        "state_code": "PE",
        "latitude": -8.04756,
        "longitude": -34.87700,
    },
    "Teresina": {
        "state": "Piaui",
        "state_code": "PI",
        "latitude": -5.08921,
        "longitude": -42.80160,
    },
    "Rio de Janeiro": {
        "state": "Rio de Janeiro",
        "state_code": "RJ",
        "latitude": -22.90680,
        "longitude": -43.17290,
    },
    "Natal": {
        "state": "Rio Grande do Norte",
        "state_code": "RN",
        "latitude": -5.79448,
        "longitude": -35.21100,
    },
    "Porto Alegre": {
        "state": "Rio Grande do Sul",
        "state_code": "RS",
        "latitude": -30.03460,
        "longitude": -51.21770,
    },
    "Porto Velho": {
        "state": "Rondonia",
        "state_code": "RO",
        "latitude": -8.76077,
        "longitude": -63.89990,
    },
    "Boa Vista": {
        "state": "Roraima",
        "state_code": "RR",
        "latitude": 2.82384,
        "longitude": -60.67530,
    },
    "Florianopolis": {
        "state": "Santa Catarina",
        "state_code": "SC",
        "latitude": -27.59540,
        "longitude": -48.54800,
    },
    "Sao Paulo": {
        "state": "Sao Paulo",
        "state_code": "SP",
        "latitude": -23.55050,
        "longitude": -46.63330,
    },
    "Aracaju": {
        "state": "Sergipe",
        "state_code": "SE",
        "latitude": -10.94720,
        "longitude": -37.07310,
    },
    "Palmas": {
        "state": "Tocantins",
        "state_code": "TO",
        "latitude": -10.24910,
        "longitude": -48.32430,
    },
}


AIR_QUALITY_VARIABLES = [
    "pm10",
    "pm2_5",
    "carbon_monoxide",
    "carbon_dioxide",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "ozone",
    "aerosol_optical_depth",
    "dust",
    "uv_index",
    "uv_index_clear_sky",
    "methane",
    "european_aqi",
    "european_aqi_pm2_5",
    "european_aqi_pm10",
    "european_aqi_nitrogen_dioxide",
    "european_aqi_ozone",
    "european_aqi_sulphur_dioxide",
    "us_aqi",
    "us_aqi_pm2_5",
    "us_aqi_pm10",
    "us_aqi_nitrogen_dioxide",
    "us_aqi_ozone",
    "us_aqi_sulphur_dioxide",
    "us_aqi_carbon_monoxide",
]