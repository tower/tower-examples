/* Table: issues_event */
{{
    config(
        materialized='incremental'
    )
}}
SELECT
    t._dlt_load_id as orig_load_id,
    t.repo__id,
    t.repo__name,
    COUNT(1) as issues_count

FROM  {{ ref('stg_issues_event') }} as t
GROUP BY orig_load_id, repo__id, repo__name
