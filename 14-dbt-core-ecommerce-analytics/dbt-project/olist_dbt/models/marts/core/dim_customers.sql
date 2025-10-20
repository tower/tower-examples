with customers as (
    select * from {{ ref('stg_customers') }}
), geo as (
    select zip_prefix, avg(lat) as lat, avg(lng) as lng
    from {{ ref('stg_geolocation') }}
    group by 1
)
select
    c.customer_id,
    c.customer_unique_id,
    c.customer_zip_prefix,
    c.customer_city,
    c.customer_state,
    g.lat,
    g.lng
from customers c
left join geo g on g.zip_prefix = c.customer_zip_prefix
