with src as (
    select * from {{ ref('olist_sellers_dataset') }}
)
select
    seller_id,
    cast(seller_zip_code_prefix as int) as seller_zip_prefix,
    seller_city,
    seller_state
from src
