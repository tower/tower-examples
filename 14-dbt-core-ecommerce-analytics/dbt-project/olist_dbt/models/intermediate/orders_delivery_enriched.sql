with orders as (
    select * from {{ ref('stg_orders') }}
)
select
    order_id,
    order_purchase_ts,
    order_estimated_delivery_date,
    order_delivered_customer_ts,
    datediff('day', order_purchase_ts, order_delivered_customer_ts) as days_to_delivery,
    datediff('day', order_estimated_delivery_date, order_delivered_customer_ts) as days_late
from orders
