select 1
from   dual
where  sysdate > sysdate - interval '2' hour;

select sysdate - interval '3' year
from   dual;

select interval '2 3:04:11.333' day to second
from   dual;

select 1
from   dual
where  sysdate > to_date('01/01/1970', 'dd/mm/yyyy') + interval '600' month;

select sysdate + interval '10' minute
from   dual;
