{{ config(materialization="view") }}

{{ my_headers() }}

select *
from table_a
