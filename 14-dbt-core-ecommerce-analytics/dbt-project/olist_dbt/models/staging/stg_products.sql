with products as (
    select * from {{ ref('olist_products_dataset') }}
), eng as (
    select * from {{ ref('product_category_name_translation') }}
)
select
    p.product_id,
    coalesce(e.product_category_name_english, p.product_category_name) as product_category,
    cast(p.product_weight_g as int) as product_weight_g,
    cast(p.product_length_cm as int) as product_length_cm,
    cast(p.product_height_cm as int) as product_height_cm,
    cast(p.product_width_cm as int) as product_width_cm
from products p
left join eng e on e.product_category_name = p.product_category_name
