/* Table: issues_event */
{{
    config(
        materialized='incremental'
    )
}}
SELECT
    t._dlt_load_id as orig_load_id,
    t.actor__id,
    t.actor__display_login,
    COUNT(1) as issues_count

FROM  {{ ref('stg_issues_event') }} as t
GROUP BY orig_load_id, actor__id, actor__display_login