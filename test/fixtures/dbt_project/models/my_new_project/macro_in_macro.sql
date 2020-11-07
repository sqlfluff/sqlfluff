-- Issue #335
{{ my_default_config("table") }}

with

source_data as (
    select "hello_world" as hello_world
)

select *
from source_data
