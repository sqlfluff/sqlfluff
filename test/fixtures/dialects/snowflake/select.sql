SELECT a FROM b;

SELECT view FROM foo;

SELECT view FROM case;

SELECT issue FROM issue;

SELECT
    customer_id,
    TRIM(value:cross) AS cross
FROM my_table;

SELECT
    customer_id
FROM my_table cross join my_table2;

select notify from foo;

select
    coalesce(do.a, do.b) as value
from delivery_override as do
;

SELECT
      t.id
    , TRUE AS test
FROM mytable t
ORDER BY TRUE
;

select
    limit as renamed
from sometable;
