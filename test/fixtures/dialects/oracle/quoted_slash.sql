select a.column_a || '\' || a.column_b test
from   test_table a;

select *
from   test_table a
where  a.column_a || '\' || a.column_b = '10\10';

select 'Test\ '
from   dual;

select '\Test\'
from   dual;
