if ((select count(*) from table1) = 0) then
set @errmsg = '';
select 1;
end if;
