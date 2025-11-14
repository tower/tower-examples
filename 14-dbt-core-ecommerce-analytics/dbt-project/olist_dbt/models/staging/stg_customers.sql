with src as (
    select * from {{ ref('olist_customers_dataset') }}
)
select
    customer_id,
    customer_unique_id,
    cast(customer_zip_code_prefix as int) as customer_zip_prefix,
    customer_city,
    customer_state
from src
