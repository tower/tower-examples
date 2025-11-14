{{ config(materialized='table') }}

{% set start_date = "cast('" ~ var('start_date') ~ "' as date)" %}
{% set end_date = "cast('" ~ var('end_date') ~ "' as date)" %}

with spine as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date=start_date,
        end_date=end_date
    ) }}
)
select
    date_day as date_day,
    date_part('year', date_day) as year,
    date_part('quarter', date_day) as quarter,
    date_part('month', date_day) as month,
    date_part('day', date_day) as day,
    strftime(date_day, '%Y-%m') as year_month,
    strftime(date_day, '%W') as week_of_year,
    case when extract(dow from date_day) in (0,6) then true else false end as is_weekend
from spine
