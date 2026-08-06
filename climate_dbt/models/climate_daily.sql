{{ config(materialized='table') }}

SELECT
    city,
    measurement_date,

    AVG(temperature_c)::numeric(5, 2)
        AS temperature_avg,

    MIN(temperature_c)
        AS temperature_min,

    MAX(temperature_c)
        AS temperature_max,

    AVG(pm2_5)::numeric(12, 3)
        AS pm2_5_avg,

    MAX(pm2_5)
        AS pm2_5_max,

    AVG(pm10)::numeric(12, 3)
        AS pm10_avg,

    MAX(pm10)
        AS pm10_max,

    AVG(ozone)::numeric(12, 3)
        AS ozone_avg,

    AVG(nitrogen_dioxide)::numeric(12, 3)
        AS nitrogen_dioxide_avg,

    AVG(sulphur_dioxide)::numeric(12, 3)
        AS sulphur_dioxide_avg,

    AVG(carbon_monoxide)::numeric(12, 3)
        AS carbon_monoxide_avg,

    MAX(uv_index)
        AS uv_index_max,

    AVG(aqi)::numeric(8, 2)
        AS aqi_avg,

    MAX(aqi)
        AS aqi_max,

    AVG(european_aqi)::numeric(8, 2)
        AS european_aqi_avg,

    MAX(european_aqi)
        AS european_aqi_max,

    COUNT(*)::integer
        AS hourly_records

FROM {{ ref('climate_hourly') }}

GROUP BY
    city,
    measurement_date