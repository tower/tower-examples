{{
  config(
    contract={'enforced': true},
    unique_key=['order_id', 'order_item_id'],
    on_schema_change='append_new_columns'
  )
}}

with items as (
    select * from {{ ref('stg_order_items') }}
), orders as (
    select * from {{ ref('stg_orders') }}
), pay as (
    select * from {{ ref('order_payments_agg') }}
), deliv as (
    select * from {{ ref('orders_delivery_enriched') }}
)
select
    i.order_id,
    i.order_item_id,
    i.product_id,
    i.seller_id,
    o.customer_id,
    o.order_purchase_ts,
    i.price,
    i.freight_value,
    i.price + i.freight_value as item_revenue,
    p.total_payment_value,
    p.max_installments,
    p.primary_payment_type,
    d.days_to_delivery,
    d.days_late
from items i
left join orders o on o.order_id = i.order_id
left join pay p on p.order_id = i.order_id
left join deliv d on d.order_id = i.order_id
