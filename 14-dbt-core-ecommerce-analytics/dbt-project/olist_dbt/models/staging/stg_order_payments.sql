with src as (
    select * from {{ ref('olist_order_payments_dataset') }}
)
select
    order_id,
    payment_sequential,
    lower(payment_type) as payment_type,
    cast(payment_installments as int) as payment_installments,
    cast(payment_value as numeric) as payment_value
from src
