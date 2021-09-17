{{
  config(
    materialized = "incremental",
    unique_key = 'id'
  )
}}

-- Test macro loading from folder.
select distinct on (id)
  (json -> 'type' ->> 'id')::int   as id,
  (json -> 'type' ->> 'name')      as name
from {{ sb_incremental(this, 'sb_route_events') }} as e
