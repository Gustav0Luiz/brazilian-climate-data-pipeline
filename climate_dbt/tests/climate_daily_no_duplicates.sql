SELECT
    city,
    measurement_date,
    COUNT(*) AS total_records

FROM {{ ref('climate_daily') }}

GROUP BY
    city,
    measurement_date

HAVING COUNT(*) > 1