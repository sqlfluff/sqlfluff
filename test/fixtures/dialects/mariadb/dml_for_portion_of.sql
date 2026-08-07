-- Application-time period DML with FOR PORTION OF.
-- https://mariadb.com/kb/en/application-time-periods/

DELETE FROM t1
FOR PORTION OF date_period
    FROM '2001-01-01' TO '2018-01-01';

UPDATE t1 FOR PORTION OF date_period
  FROM '2000-01-01' TO '2018-01-01'
SET name = CONCAT(name, '_original');
