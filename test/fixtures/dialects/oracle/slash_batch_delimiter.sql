create or replace view example as
select smthng
from smwhr
/

comment on table example is 'abc'
/

create or replace public synonym example for example
/

create or replace view v_division as
select 1 / 100 as z from dual
/

create or replace view v_semicolon as
select sysdate - 1/24 as hh from dual;
