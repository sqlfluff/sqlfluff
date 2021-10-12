if ((select count(*) from table) = 0 and x = 1) then
set @errmsg = '';
select 1;
end if;