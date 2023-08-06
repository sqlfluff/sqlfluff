create view sales_vw as
select * from public.sales
union all
select * from spectrum.sales
with no schema binding;


create materialized view mat_view_example
backup yes
auto refresh no
as 
select col1
from example_table
;