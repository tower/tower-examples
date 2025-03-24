/* check if the destination already has a list of processed ids
if not we will process all loads with status 0 (==success) */
{% set active_ids_exist = adapter.get_relation(
        database=this.database ,
        schema=this.schema,
        identifier="dlt_processed_load_ids" ) %}

SELECT load_id FROM {{  source('raw_data', '_dlt_loads') }}
WHERE status = 0
/* exclude already processed load_ids */
{% if active_ids_exist and not should_full_refresh() %}
AND load_id NOT IN (SELECT load_id FROM {{ source('transformed_data', 'dlt_processed_load_ids') }})
{% endif %}