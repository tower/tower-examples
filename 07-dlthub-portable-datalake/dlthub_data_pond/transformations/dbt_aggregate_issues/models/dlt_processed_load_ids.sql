{{
    config(
        materialized='incremental'
    )
}}
-- depends_on: {{ ref('dim__dlt_loads') }}
-- depends_on: {{ ref('dim_issues_actors') }}
-- depends_on: {{ ref('dim_issues_repos') }}
/* we save all currently active load ids into the processed ids table */
select load_id, {{ current_timestamp() }} as inserted_at FROM {{ ref('dlt_active_load_ids') }}