SELECT
    city,
    measurement_date,
    hourly_records

FROM {{ ref('climate_daily') }}

WHERE hourly_records <> 24