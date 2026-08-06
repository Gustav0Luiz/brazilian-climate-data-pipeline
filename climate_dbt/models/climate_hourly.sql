{{ config(materialized='table') }}

SELECT
    temperature.city,
    temperature.latitude,
    temperature.longitude,
    temperature.measured_at_local,
    temperature.measured_at_local::date AS measurement_date,
    EXTRACT(HOUR FROM temperature.measured_at_local)::integer
        AS measurement_hour,
    temperature.timezone,
    temperature.temperature_c,

    air.elevation,
    air.pm10,
    air.pm2_5,
    air.carbon_monoxide,
    air.carbon_dioxide,
    air.nitrogen_dioxide,
    air.sulphur_dioxide,
    air.ozone,
    air.methane,
    air.aerosol_optical_depth,
    air.dust,
    air.uv_index,
    air.uv_index_clear_sky,

    air.european_aqi,
    air.european_aqi_pm2_5,
    air.european_aqi_pm10,
    air.european_aqi_nitrogen_dioxide,
    air.european_aqi_ozone,
    air.european_aqi_sulphur_dioxide,

    air.aqi,
    air.aqi_pm2_5,
    air.aqi_pm10,
    air.aqi_nitrogen_dioxide,
    air.aqi_ozone,
    air.aqi_sulphur_dioxide,
    air.aqi_carbon_monoxide,

    temperature.collected_at AS temperature_collected_at,
    air.collected_at AS air_quality_collected_at

FROM {{ source('raw', 'raw_temperature') }} AS temperature

INNER JOIN {{ source('raw', 'raw_air_quality') }} AS air
    ON air.city = temperature.city
   AND air.measured_at_local = temperature.measured_at_local