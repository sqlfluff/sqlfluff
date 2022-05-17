select 1 into @dumpfile from table;

SELECT name
INTO @name
FROM t
WHERE id = 1;

SELECT name
FROM t
WHERE id = 1
INTO @name;
