if (x = 0) then
set @errmsg = '';
select 1;
elseif (x = 1) then
set _test = 1;
else
select 2;
end if;
