SELECT
    city,
    measured_at_local,
    COUNT(*) AS total_records

FROM {{ ref('climate_hourly') }}

GROUP BY
    city,
    measured_at_local

HAVING COUNT(*) > 1