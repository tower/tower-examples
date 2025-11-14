with p as (
    select * from {{ ref('stg_products') }}
)
select
    p.product_id,
    p.product_category,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm,
    (p.product_length_cm * p.product_height_cm * p.product_width_cm) / 1000000.0 as product_volume_m3
from p
