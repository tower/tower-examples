# dbt-core Olist (Brazilian E‑commerce) – Starter Analytics Project

A production-style dbt project you can run locally against **DuckDB** (default) or **Postgres**, using the Kaggle Olist dataset. Includes seeds (raw CSVs), staging models, dims/facts, snapshots, packages, tests, and docs.

> Folder tree (high level)
```
olist_dbt/
├─ README.md
├─ dbt_project.yml
├─ packages.yml
├─ profiles.example.yml
├─ macros/
│  └─ readme.md
├─ seeds/
│  ├─ olist_customers_dataset.csv
│  ├─ olist_geolocation_dataset.csv
│  ├─ olist_order_items_dataset.csv
│  ├─ olist_order_payments_dataset.csv
│  ├─ olist_order_reviews_dataset.csv
│  ├─ olist_orders_dataset.csv
│  ├─ olist_products_dataset.csv
│  └─ product_category_name_translation.csv
├─ models/
│  ├─ sources.yml                     # optional if you load to a "raw" schema instead of seeds
│  ├─ staging/
│  │  ├─ schema.yml
│  │  ├─ stg_customers.sql
│  │  ├─ stg_orders.sql
│  │  ├─ stg_order_items.sql
│  │  ├─ stg_order_payments.sql
│  │  ├─ stg_order_reviews.sql
│  │  ├─ stg_products.sql
│  │  ├─ stg_sellers.sql
│  │  └─ stg_geolocation.sql
│  ├─ intermediate/
│  │  ├─ order_payments_agg.sql
│  │  └─ orders_delivery_enriched.sql
│  └─ marts/
│     ├─ core/
│     │  ├─ dim_date.sql
│     │  ├─ dim_customers.sql
│     │  ├─ dim_sellers.sql
│     │  ├─ dim_products.sql
│     │  ├─ dim_geography.sql
│     │  ├─ fact_order_items.sql
│     │  └─ schema.yml
│     └─ exposures.yml
└─ snapshots/
   ├─ customer_snapshot.sql
   └─ seller_snapshot.sql
```

---

## 1) README.md
```md
# Olist (Brazilian E‑commerce) · dbt-core Analytics Project

This project builds a clean star schema over the Kaggle Olist dataset using dbt Core (v1.10+). It ships with:

- **Seeds**: load CSVs into your warehouse or DuckDB file
- **Staging**: type casting, naming, basic cleaning
- **Intermediate**: payment aggregation & delivery KPIs
- **Marts**: star schema (dims + fact)
- **Snapshots**: track slowly changing customer/seller details
- **Tests**: generic and package tests
- **Docs**: auto-generated catalog & lineage graph

## Quickstart (DuckDB)
1. Install
   ```bash
   python -m pip install "dbt-core==1.10.*" dbt-duckdb
   ```
2. Clone and download data
   ```bash
   git clone <this repo>
   cd olist_dbt
   # Download Kaggle Olist CSVs and drop them into ./seeds (filenames must match)
   ```
3. Profile
   Copy `profiles.example.yml` to `~/.dbt/profiles.yml` and keep the `duckdb` target.
4. Run
   ```bash
   dbt deps
   dbt seed  # loads CSVs as tables
   dbt build # run + test
   dbt docs generate && dbt docs serve
   ```

## Postgres Variant
1. Install
   ```bash
   python -m pip install "dbt-core==1.10.*" "dbt-postgres==1.10.*"
   ```
2. In `~/.dbt/profiles.yml`, use the `postgres` target from `profiles.example.yml` and ensure the database has a schema (e.g. `raw`) and permissions.
3. Either `dbt seed` (keep using seeds) **or** load the CSVs to your Postgres `raw` schema via your preferred tool and switch staging models to read from `source()` (see comments in staging SQL files).

## Default Star Schema
- **Fact**: `fact_order_items` (grain: order_id + order_item_id)
- **Dims**: `dim_customers`, `dim_sellers`, `dim_products`, `dim_geography`, `dim_date`
- **Intermediate**: `order_payments_agg` (per-order rollup), `orders_delivery_enriched` (KPI calc)

## KPIs & Examples
- Revenue = price + freight
- Delivery time = delivered_date − purchase_date
- Delivery delay = delivered_date − estimated_delivery_date
- NPS-like score from `review_score`

```

---

## 2) dbt_project.yml
```yaml
name: 'olist_dbt'
version: '1.0.0'
config-version: 2
require-dbt-version:
  - ">=1.10.0"
  - "<2.0.0"

profile: 'olist'

model-paths: ["models"]
seed-paths: ["seeds"]
macro-paths: ["macros"]

models:
  olist_dbt:
    +materialized: view
    staging:
      +tags: ['staging']
    intermediate:
      +materialized: table
      +tags: ['intermediate']
    marts:
      +materialized: table
      core:
        +tags: ['mart', 'core']

seeds:
  olist_dbt:
    +quote_columns: false
    +column_types:
      olist_order_items_dataset:
        price: numeric
        freight_value: numeric
      olist_order_payments_dataset:
        payment_value: numeric
      olist_orders_dataset:
        order_purchase_timestamp: timestamp
        order_approved_datetime: timestamp
        order_delivered_carrier_date: timestamp
        order_delivered_customer_date: timestamp
        order_estimated_delivery_date: date

vars:
  start_date: '2016-01-01'
  end_date: '2018-12-31'
```

---

## 3) packages.yml
```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: ">=1.3.0,<2.0.0"
  - package: metaplane/dbt_expectations
    version: ">=0.10.5,<1.0.0"  # optional; comment out if you don't want it
```

---

## 4) profiles.example.yml
```yaml
olist:
  target: duckdb
  outputs:
    duckdb:
      type: duckdb
      path: ".db/olist.duckdb"   # will be created locally
      schema: analytics
    postgres:
      type: postgres
      host: localhost
      user: olist
      password: olist
      dbname: olist
      port: 5432
      schema: analytics
      threads: 4
```

---

## 5) models/sources.yml (optional if you use seeds)
```yaml
version: 2
sources:
  - name: raw
    schema: raw
    tables:
      - name: olist_orders_dataset
      - name: olist_order_items_dataset
      - name: olist_order_payments_dataset
      - name: olist_order_reviews_dataset
      - name: olist_customers_dataset
      - name: olist_sellers_dataset
      - name: olist_products_dataset
      - name: olist_geolocation_dataset
      - name: product_category_name_translation
```

---

## 6) models/staging/schema.yml
```yaml
version: 2
models:
  - name: stg_orders
    description: Cleaned orders with consistent types and timestamps.
    columns:
      - name: order_id
        tests: [unique, not_null]
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('stg_customers')
              field: customer_id
      - name: order_status
        tests:
          - accepted_values:
              values: ["approved", "delivered", "shipped", "canceled", "invoiced", "processing", "unavailable"]
  - name: stg_order_items
    columns:
      - name: order_id
        tests:
          - relationships:
              to: ref('stg_orders')
              field: order_id
      - name: order_item_id
        tests: [not_null]
  - name: stg_order_payments
    columns:
      - name: order_id
        tests:
          - relationships:
              to: ref('stg_orders')
              field: order_id
  - name: stg_order_reviews
    columns:
      - name: order_id
        tests:
          - relationships:
              to: ref('stg_orders')
              field: order_id
  - name: stg_customers
    columns:
      - name: customer_id
        tests: [unique, not_null]
  - name: stg_sellers
    columns:
      - name: seller_id
        tests: [unique, not_null]
  - name: stg_products
    columns:
      - name: product_id
        tests: [unique, not_null]
```

---

## 7) models/staging/*.sql

> Each staging model reads from **seeds** via `ref()`; if you instead ingested CSVs to a `raw` schema, swap the `from` CTE to use `source('raw','...')`.

### stg_orders.sql
```sql
with src as (
    select * from {{ ref('olist_orders_dataset') }}
    -- (or: select * from {{ source('raw','olist_orders_dataset') }})
)
select
    order_id,
    customer_id,
    lower(order_status) as order_status,
    cast(order_purchase_timestamp as timestamp) as order_purchase_ts,
    cast(order_approved_datetime as timestamp) as order_approved_ts,
    cast(order_delivered_carrier_date as timestamp) as order_delivered_carrier_ts,
    cast(order_delivered_customer_date as timestamp) as order_delivered_customer_ts,
    cast(order_estimated_delivery_date as date) as order_estimated_delivery_date
from src
```

### stg_order_items.sql
```sql
with src as (
    select * from {{ ref('olist_order_items_dataset') }}
)
select
    order_id,
    order_item_id,
    product_id,
    seller_id,
    cast(shipping_limit_date as timestamp) as shipping_limit_ts,
    cast(price as numeric) as price,
    cast(freight_value as numeric) as freight_value
from src
```

### stg_order_payments.sql
```sql
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
```

### stg_order_reviews.sql
```sql
with src as (
    select * from {{ ref('olist_order_reviews_dataset') }}
)
select
    review_id,
    order_id,
    cast(review_score as int) as review_score,
    review_comment_title,
    review_comment_message,
    cast(review_creation_date as timestamp) as review_creation_ts,
    cast(review_answer_timestamp as timestamp) as review_answer_ts
from src
```

### stg_customers.sql
```sql
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
```

### stg_sellers.sql
```sql
with src as (
    select * from {{ ref('olist_sellers_dataset') }}
)
select
    seller_id,
    cast(seller_zip_code_prefix as int) as seller_zip_prefix,
    seller_city,
    seller_state
from src
```

### stg_products.sql
```sql
with products as (
    select * from {{ ref('olist_products_dataset') }}
),
eng as (
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
left join eng e
  on e.product_category_name = p.product_category_name
```

### stg_geolocation.sql
```sql
with src as (
    select * from {{ ref('olist_geolocation_dataset') }}
)
select
    cast(geolocation_zip_code_prefix as int) as zip_prefix,
    geolocation_city as city,
    geolocation_state as state,
    cast(geolocation_lat as double) as lat,
    cast(geolocation_lng as double) as lng
from src
```

---

## 8) models/intermediate

### order_payments_agg.sql
```sql
with payments as (
  select * from {{ ref('stg_order_payments') }}
)
select
  order_id,
  sum(payment_value)                            as total_payment_value,
  max(payment_installments)                     as max_installments,
  any_value(payment_type)                       as primary_payment_type,
  count(*)                                      as payment_rows
from payments
group by 1
```

### orders_delivery_enriched.sql
```sql
with orders as (
  select * from {{ ref('stg_orders') }}
)
select
  order_id,
  order_purchase_ts,
  order_estimated_delivery_date,
  order_delivered_customer_ts,
  datediff('day', order_purchase_ts, order_delivered_customer_ts)         as days_to_delivery,
  datediff('day', order_estimated_delivery_date, order_delivered_customer_ts) as days_late
from orders
```

> Note: `datediff` syntax works on DuckDB/Postgres; adjust if your adapter differs.

---

## 9) models/marts/core/dimensions & facts

### dim_date.sql
```sql
with spine as (
  {{ dbt_utils.date_spine(
       datepart='day',
       start_date=to_date('{{ var("start_date") }}'),
       end_date=to_date('{{ var("end_date") }}')) }}
)
select
  date_day                                    as date,
  extract(year from date_day)::int            as year,
  extract(month from date_day)::int           as month,
  extract(day from date_day)::int             as day,
  to_char(date_day, 'YYYY-MM')                as year_month
from spine
```

### dim_geography.sql
```sql
with geo as (
  select * from {{ ref('stg_geolocation') }}
)
select
  zip_prefix,
  any_value(city)  as city,
  any_value(state) as state,
  avg(lat)         as lat,
  avg(lng)         as lng
from geo
group by 1
```

### dim_customers.sql
```sql
with c as (
  select * from {{ ref('stg_customers') }}
), g as (
  select * from {{ ref('dim_geography') }}
)
select
  c.customer_id,
  c.customer_unique_id,
  c.customer_city,
  c.customer_state,
  c.customer_zip_prefix,
  g.lat, g.lng
from c
left join g on g.zip_prefix = c.customer_zip_prefix
```

### dim_sellers.sql
```sql
with s as (
  select * from {{ ref('stg_sellers') }}
), g as (
  select * from {{ ref('dim_geography') }}
)
select
  s.seller_id,
  s.seller_city,
  s.seller_state,
  s.seller_zip_prefix,
  g.lat, g.lng
from s
left join g on g.zip_prefix = s.seller_zip_prefix
```

### dim_products.sql
```sql
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
```

### fact_order_items.sql
```sql
{{
  config(
    contract = {"enforced": true},
    unique_key = ["order_id", "order_item_id"],
    on_schema_change = "append_new_columns"
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
  i.price + i.freight_value                 as item_revenue,
  p.total_payment_value,
  p.max_installments,
  p.primary_payment_type,
  d.days_to_delivery,
  d.days_late
from items i
left join orders o on o.order_id = i.order_id
left join pay    p on p.order_id = i.order_id
left join deliv  d on d.order_id = i.order_id
```

### marts/core/schema.yml
```yaml
version: 2
models:
  - name: dim_customers
    description: One row per customer_id, enriched with geolocation.
    columns:
      - name: customer_id
        tests: [unique, not_null]
  - name: dim_sellers
    columns:
      - name: seller_id
        tests: [unique, not_null]
  - name: dim_products
    columns:
      - name: product_id
        tests: [unique, not_null]
  - name: fact_order_items
    description: Order-item grain fact table with revenue and delivery KPIs.
    columns:
      - name: order_id
        tests:
          - relationships:
              to: ref('stg_orders')
              field: order_id
      - name: order_item_id
        tests: [not_null]
      - name: item_revenue
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= 0"
```

---

## 10) snapshots

### snapshots/customer_snapshot.sql
```sql
{% snapshot customer_snapshot %}
{{
  config(
    target_schema='snapshots',
    unique_key='customer_id',
    strategy='check',
    check_cols=['customer_city','customer_state','customer_zip_prefix']
  )
}}
select * from {{ ref('stg_customers') }}
{% endsnapshot %}
```

### snapshots/seller_snapshot.sql
```sql
{% snapshot seller_snapshot %}
{{
  config(
    target_schema='snapshots',
    unique_key='seller_id',
    strategy='check',
    check_cols=['seller_city','seller_state','seller_zip_prefix']
  )
}}
select * from {{ ref('stg_sellers') }}
{% endsnapshot %}
```

---

## 11) models/marts/exposures.yml (optional)
```yaml
version: 2
exposures:
  - name: olist_core_look
    type: dashboard
    maturity: low
    url: https://bi.example.com/dashboards/olist-core
    description: Core Olist KPI dashboard consuming dim_* and fact_order_items
    depends_on:
      - ref('fact_order_items')
      - ref('dim_customers')
      - ref('dim_products')
      - ref('dim_sellers')
      - ref('dim_geography')
    owner:
      name: Data Team
      email: data@example.com
```

---

## 12) macros/readme.md
```md
This project relies primarily on `dbt_utils`. Add custom macros here if you need adapter-specific tweaks (e.g., date math, currency formatting).
```

---

## Notes & Extensions
- If you prefer a single **fact_orders** model, add a per-order rollup over `stg_order_items` and join payments/reviews there.
- Add **service level** dims (e.g., delivery performance buckets) using `days_late` columns.
- Consider **incremental** materializations if you’re ingesting Olist data regularly.
- If your warehouse supports **grants**, set `+grants:` at the model level to manage permissions.
- Use `dbt docs generate` to view the DAG and data dictionary.

