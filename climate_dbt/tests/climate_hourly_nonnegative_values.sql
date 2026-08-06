SELECT
    city,
    measured_at_local,
    pm2_5,
    pm10,
    aqi,
    european_aqi

FROM {{ ref('climate_hourly') }}

WHERE
       pm2_5 < 0
    OR pm10 < 0
    OR aqi < 0
    OR european_aqi < 0