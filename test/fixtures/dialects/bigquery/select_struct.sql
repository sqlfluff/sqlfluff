-- Example of "select as struct *" syntax.
select
  some_table.foo_id,
  array(
    select as struct *
    from another_table
    where another_table.foo_id = some_table.foo_id
  )
from another_table;

-- Example of "select as struct <<column list>>" syntax
select as struct
  '1' as bb,
  2 as aa;

select distinct as struct
    '1' as bb,
    2 as aa;

-- Example of explicitly building a struct in a select clause.
select
  struct(
    bar.bar_id as id,
    bar.bar_name as bar
  ) as bar
from foo
left join bar on bar.foo_id = foo.foo_id;

-- Array of structs
SELECT
  col_1,
  col_2
FROM
  UNNEST(ARRAY<STRUCT<col_1 STRING, col_2 STRING>>[
      ('hello','world'),
      ('hi', 'there')
      ]);

SELECT
  STRUCT<int64>(5),
  STRUCT<date>("2011-05-05"),
  STRUCT<x int64, y string>(1, t.str_col),
  STRUCT<int64>(int_col);

-- This is to test typeless struct fields are not mistakenly considered as
-- data types, see https://github.com/sqlfluff/sqlfluff/issues/3277
SELECT
  STRUCT(
    some_field,
    some_other_field
  ) AS col
FROM table;

-- Empty STRUCT within TO_JSON
SELECT
  TO_JSON(STRUCT()) AS col
FROM table;
