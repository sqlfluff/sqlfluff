select case when "Spec\"s 23" like 'Spec\'s%' then 'boop' end as field;

select 'This shouldn''t fail' as success;
