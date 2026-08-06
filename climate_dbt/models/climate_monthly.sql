{{ config(materialized='table') }}

WITH hourly_data AS (

    SELECT
        *,
        DATE_TRUNC(
            'month',
            measured_at_local
        )::date AS measurement_month

    FROM {{ ref('climate_hourly') }}

)

SELECT
    city,
    measurement_month,

    EXTRACT(YEAR FROM measurement_month)::integer
        AS measurement_year,

    EXTRACT(MONTH FROM measurement_month)::integer
        AS measurement_month_number,

    ROUND(AVG(temperature_c), 2)
        AS temperature_avg,

    MIN(temperature_c)
        AS temperature_min,

    MAX(temperature_c)
        AS temperature_max,

    ROUND(AVG(pm2_5), 3)
        AS pm2_5_avg,

    MAX(pm2_5)
        AS pm2_5_max,

    ROUND(AVG(pm10), 3)
        AS pm10_avg,

    MAX(pm10)
        AS pm10_max,

    ROUND(AVG(ozone), 3)
        AS ozone_avg,

    MAX(ozone)
        AS ozone_max,

    ROUND(AVG(nitrogen_dioxide), 3)
        AS nitrogen_dioxide_avg,

    ROUND(AVG(sulphur_dioxide), 3)
        AS sulphur_dioxide_avg,

    ROUND(AVG(carbon_monoxide), 3)
        AS carbon_monoxide_avg,

    MAX(uv_index)
        AS uv_index_max,

    ROUND(AVG(aqi), 2)
        AS aqi_avg,

    MAX(aqi)
        AS aqi_max,

    ROUND(AVG(european_aqi), 2)
        AS european_aqi_avg,

    MAX(european_aqi)
        AS european_aqi_max,

    COUNT(*)::integer
        AS hourly_records,

    COUNT(DISTINCT measurement_date)::integer
        AS days_present

FROM hourly_data

GROUP BY
    city,
    measurement_month