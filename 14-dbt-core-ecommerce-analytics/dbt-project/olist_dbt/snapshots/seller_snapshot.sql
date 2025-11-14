{% snapshot seller_snapshot %}
{{
  config(
    target_schema='snapshots',
    unique_key='seller_id',
    strategy='check',
    check_cols=['seller_city', 'seller_state', 'seller_zip_prefix']
  )
}}
select * from {{ ref('stg_sellers') }}
{% endsnapshot %}
