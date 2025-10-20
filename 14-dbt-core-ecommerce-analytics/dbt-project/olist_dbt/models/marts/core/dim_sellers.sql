with sellers as (
    select * from {{ ref('stg_sellers') }}
), geo as (
    select zip_prefix, avg(lat) as lat, avg(lng) as lng
    from {{ ref('stg_geolocation') }}
    group by 1
)
select
    s.seller_id,
    s.seller_zip_prefix,
    s.seller_city,
    s.seller_state,
    g.lat,
    g.lng
from sellers s
left join geo g on g.zip_prefix = s.seller_zip_prefix
