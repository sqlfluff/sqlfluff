if ((select count(*) from table) = 0) then
set @errmsg = '';
select 1;
end if;