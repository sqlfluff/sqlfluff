SELECT b.start, CAST(b.foo AS date) AS bar
FROM dbt.baz AS b
WHERE b.start = '2020-01-01';

SELECT start FROM tbl WHERE start > '2020-01-01';
