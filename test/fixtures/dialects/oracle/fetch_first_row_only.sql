select column_name
from   table_name
fetch  first row only;

select column_name
from   table_name
fetch  first rows only;

select column_name
from   table_name
fetch  first 2 row only;

select column_name
from   table_name
fetch  first 2 rows only;

select column_name
from   table_name
fetch  first 10 percent rows only;

select column_name
from   table_name
order by column_name
fetch  next 2.5 percent rows with ties;

select column_name
from   table_name
order by column_name
fetch  next 5 rows with ties;

-- PERCENT is non-reserved, so it can still name the row count.
select column_name
from   table_name
fetch  first percent rows only;

select column_name
from   table_name
fetch  first percent percent rows only;
