-- Issue #333
select *
from table_a
where ds = '{{ var("ds") }}'
