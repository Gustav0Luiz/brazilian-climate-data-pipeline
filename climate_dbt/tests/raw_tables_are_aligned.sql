SELECT
    temperature.city,
    temperature.measured_at_local,
    'missing_air_quality' AS problem

FROM {{ source('raw', 'raw_temperature') }} AS temperature

LEFT JOIN {{ source('raw', 'raw_air_quality') }} AS air
    ON air.city = temperature.city
   AND air.measured_at_local =
       temperature.measured_at_local

WHERE air.city IS NULL


UNION ALL


SELECT
    air.city,
    air.measured_at_local,
    'missing_temperature' AS problem

FROM {{ source('raw', 'raw_air_quality') }} AS air

LEFT JOIN {{ source('raw', 'raw_temperature') }} AS temperature
    ON temperature.city = air.city
   AND temperature.measured_at_local =
       air.measured_at_local

WHERE temperature.city IS NULL