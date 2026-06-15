select 0 as test
from sysibm.sysdummy1
for read only;

select 0 as test
from sysibm.sysdummy1
order by test
for read only;

select 0 as test
from sysibm.sysdummy1
with ur;

select 0 as test
from sysibm.sysdummy1
order by test
with ur;

select 0 as test
from sysibm.sysdummy1
for read only
with ur;

select 0 as test
from sysibm.sysdummy1
order by test
for read only
with ur;

select 0 as test
from sysibm.sysdummy1
for fetch only;

select 0 as test
from sysibm.sysdummy1
with cs;

select 0 as test
from sysibm.sysdummy1
with rs;

select 0 as test
from sysibm.sysdummy1
with rr;

select 0 as test
from sysibm.sysdummy1
for read only
with rr use and keep share locks;

select 1 as test
from sysibm.sysdummy1
union
select 2 as test
from sysibm.sysdummy1
with ur;

select 1 as test
from sysibm.sysdummy1
union
select 2 as test
from sysibm.sysdummy1
order by test
for read only
with ur;
