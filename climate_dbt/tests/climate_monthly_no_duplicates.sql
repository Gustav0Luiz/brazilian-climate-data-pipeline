SELECT
    city,
    measurement_month,
    COUNT(*) AS total_records

FROM {{ ref('climate_monthly') }}

GROUP BY
    city,
    measurement_month

HAVING COUNT(*) > 1