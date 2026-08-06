-- tabela raw de temperaturas 
CREATE TABLE IF NOT EXISTS raw_temperature (
    id BIGSERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,
    measured_at_local TIMESTAMP NOT NULL,
    timezone VARCHAR(50) NOT NULL,
    temperature_c NUMERIC(5, 2),
    collected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (city, measured_at_local)
);


-- tabela raw de qualidade do ar
CREATE TABLE IF NOT EXISTS raw_air_quality (

    id BIGSERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,

    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,
    elevation NUMERIC(8, 2),

    measured_at_local TIMESTAMP NOT NULL,
    timezone VARCHAR(50) NOT NULL,
    timezone_abbreviation VARCHAR(20),
    utc_offset_seconds INTEGER,

    pm10 NUMERIC(12, 3),
    pm2_5 NUMERIC(12, 3),

    carbon_monoxide NUMERIC(12, 3),
    carbon_dioxide NUMERIC(12, 3),
    nitrogen_dioxide NUMERIC(12, 3),
    sulphur_dioxide NUMERIC(12, 3),
    ozone NUMERIC(12, 3),
    methane NUMERIC(12, 3),

    aerosol_optical_depth NUMERIC(8, 4),
    dust NUMERIC(12, 3),

    uv_index NUMERIC(6, 2),
    uv_index_clear_sky NUMERIC(6, 2),

    european_aqi SMALLINT,
    european_aqi_pm2_5 SMALLINT,
    european_aqi_pm10 SMALLINT,
    european_aqi_nitrogen_dioxide SMALLINT,
    european_aqi_ozone SMALLINT,
    european_aqi_sulphur_dioxide SMALLINT,

    aqi SMALLINT,
    aqi_pm2_5 SMALLINT,
    aqi_pm10 SMALLINT,
    aqi_nitrogen_dioxide SMALLINT,
    aqi_ozone SMALLINT,
    aqi_sulphur_dioxide SMALLINT,
    aqi_carbon_monoxide SMALLINT,

    collected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (city, measured_at_local)
);

-- indice para acelerar os filtros por data
CREATE INDEX IF NOT EXISTS idx_raw_air_quality_measured_at
    ON raw_air_quality (measured_at_local);