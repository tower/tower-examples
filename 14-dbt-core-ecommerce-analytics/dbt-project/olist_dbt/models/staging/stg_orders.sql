with src as (
    select * from {{ ref('olist_orders_dataset') }}
    -- to read from loaded sources instead of seeds, swap to: select * from {{ source('raw', 'olist_orders_dataset') }}
)
select
    order_id,
    customer_id,
    lower(order_status) as order_status,
    cast(order_purchase_timestamp as timestamp) as order_purchase_ts,
    cast(order_approved_at as timestamp) as order_approved_ts,
    cast(order_delivered_carrier_date as timestamp) as order_delivered_carrier_ts,
    cast(order_delivered_customer_date as timestamp) as order_delivered_customer_ts,
    cast(order_estimated_delivery_date as date) as order_estimated_delivery_date
from src
