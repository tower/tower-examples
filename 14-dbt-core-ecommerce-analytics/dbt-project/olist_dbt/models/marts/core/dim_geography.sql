with geo as (
    select * from {{ ref('stg_geolocation') }}
)
select
    zip_prefix,
    city,
    state,
    avg(lat) as lat,
    avg(lng) as lng
from geo
group by 1, 2, 3
