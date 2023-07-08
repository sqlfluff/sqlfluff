-- In snowflake the column position is denoted with $n syntax (e.g. $1, $2)
-- https://docs.snowflake.com/en/sql-reference/sql/select.html#parameters
select $1 as type, $2 as price
from (values ('toffee', 5), ('starburst', 8), ('flying_saucer', 1))
