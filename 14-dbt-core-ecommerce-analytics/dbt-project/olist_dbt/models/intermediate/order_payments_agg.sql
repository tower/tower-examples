with payments as (
    select * from {{ ref('stg_order_payments') }}
)
select
    order_id,
    sum(payment_value) as total_payment_value,
    max(payment_installments) as max_installments,
    min(payment_type) as primary_payment_type,
    count(*) as payment_rows
from payments
group by 1
