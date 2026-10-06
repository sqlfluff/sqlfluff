if (x = 0) then
select 0;
if (y = 1) then
set @errmsg = '';
select 1;
end if;
end if;

if (x = 0) then
select case when a = 1 then 1 else 2 end;
end if;
