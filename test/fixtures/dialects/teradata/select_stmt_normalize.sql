select normalize on meets or overlaps
    id
    ,period(vld_fm, vld_to) as vld_prd
from mydb.mytable
where id = 12345;

SELECT NORMALIZE ON MEETS OR OVERLAPS emp_id, duration 
FROM project;

SELECT NORMALIZE project_name, duration 
FROM project;

SELECT NORMALIZE project_name, dept_id, duration 
FROM project;

SELECT NORMALIZE ON OVERLAPS project_name, dept_id, duration 
FROM project;

SELECT NORMALIZE ON OVERLAPS OR MEETS project_name, dept_id, duration 
FROM project;
