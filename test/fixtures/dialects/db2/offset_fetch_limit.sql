-- Offset
select column_name
from table_name
offset 2 row;

select column_name
from table_name
offset 2 rows;

select column_name
from table_name
offset 1 + 2 row;

select column_name
from table_name
offset 1 + 2 rows;

select column_name
from table_name
offset (1 + 2) row;

select column_name
from table_name
offset (1 + 2) rows;

-- Fetch
select column_name
from table_name
fetch first row only;

select column_name
from table_name
fetch first rows only;

select column_name
from table_name
fetch first 2 row only;

select column_name
from table_name
fetch first 2 rows only;

select column_name
from table_name
fetch first 1 + 2 row only;

select column_name
from table_name
fetch first 1 + 2 rows only;

select column_name
from table_name
fetch first (1 + 2) row only;

select column_name
from table_name
fetch first (1 + 2) rows only;

-- Offset and Fetch
select column_name
from table_name
offset 1 row
fetch first 2 row only;

select column_name
from table_name
offset 1 row
fetch first 2 rows only;

select column_name
from table_name
offset 1 + 2 row
fetch first 1 + 2 row only;

select column_name
from table_name
offset 1 + 2 row
fetch first 1 + 2 rows only;

-- Limit alternative syntax
select column_name
from table_name
limit 1;

select column_name
from table_name
limit 2 offset 1;

select column_name
from table_name
limit 1, 2;
