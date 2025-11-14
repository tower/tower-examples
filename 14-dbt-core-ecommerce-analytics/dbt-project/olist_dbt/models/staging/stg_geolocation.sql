with src as (
    select * from {{ ref('olist_geolocation_dataset') }}
)
select
    cast(geolocation_zip_code_prefix as int) as zip_prefix,
    geolocation_city as city,
    geolocation_state as state,
    cast(geolocation_lat as double) as lat,
    cast(geolocation_lng as double) as lng
from src
