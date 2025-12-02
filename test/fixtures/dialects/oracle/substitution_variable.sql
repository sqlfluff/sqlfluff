grant select on my_table to &REGISTRY;

SELECT &SORTCOL, SALARY
FROM &MYTABLE
WHERE SALARY>12000;

select employee_id from employees where last_name = '&myv';

select * from employees where employee_id = &myv;

SELECT SALARY FROM EMP_DETAILS_VIEW WHERE EMPLOYEE_ID='&X.5';

SELECT &GROUP_COL, MAX(&NUMBER_COL) MAXIMUM
FROM &MY_TABLE
GROUP BY &GROUP_COL;

select * from employees where employee_id = &&myv;

insert into mytable values (&myv);
