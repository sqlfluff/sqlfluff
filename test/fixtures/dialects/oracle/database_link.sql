select * from foo@bar where 1 = 1;

select baz.name from foo@bar baz where 1 = 1;

select function_a@orcl()
from   dual;

select pkg_test.function_a@orcl(1)
from   dual;
