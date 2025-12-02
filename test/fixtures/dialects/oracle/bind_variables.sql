select :abc
from   dual;

insert into mytab values(:abc,:xyz);

select column_name
from   table_name
where  column_name = :column_name_filter;
