select
lag(test)
over (ORDER BY test)
from schema.test_table;

select
lag(test)
over (PARTITION BY test ORDER BY test)
from schema.test_table;
