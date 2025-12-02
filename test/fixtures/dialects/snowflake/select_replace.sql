select * replace ('DEPT-' || department_id as department_id) from table1;

select * replace ('prefix1' || col1 as alias1, 'prefix2' || col2 as alias2) from table1;
