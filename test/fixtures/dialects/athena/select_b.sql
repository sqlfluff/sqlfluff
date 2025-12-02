WITH with_query as (
  select
   field_1,
   field_2
  from table_1)

select
  field_1,
  field_2,
  count(1)
from with_query
where field_1 = 'value'
group by 1, 2
having count(1) > 10
order by 1 DESC
limit 10;
