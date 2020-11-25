-- Issue #333
select *
from table_a
where ds = date '{{ var("ds") }}'
