/* Table: _dlt_loads */
/* Description: Created by DLT. Tracks completed loads */
{{
    config(
        materialized='view'
    )
}}
-- depends_on: {{ ref('dlt_active_load_ids') }}

SELECT
/* select which columns will be available for table '_dlt_loads' */
    load_id,
    schema_name,
    status,
    inserted_at,
    schema_version_hash,
FROM {{ source('raw_data', '_dlt_loads') }}
