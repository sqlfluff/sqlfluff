if ((select count(*) from table1) = 0 and x = 1) then
set @errmsg = '';
select 1;
end if;
