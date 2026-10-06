-- Querying system-versioned tables with FOR SYSTEM_TIME.
-- https://mariadb.com/kb/en/system-versioned-tables/

SELECT * FROM t FOR SYSTEM_TIME AS OF TIMESTAMP'2016-10-09 08:07:06';

SELECT * FROM t FOR SYSTEM_TIME BETWEEN (NOW() - INTERVAL 1 YEAR) AND NOW();

SELECT * FROM t FOR SYSTEM_TIME FROM '2016-01-01 00:00:00' TO '2017-01-01 00:00:00';

SELECT * FROM t FOR SYSTEM_TIME ALL;

-- With an alias and a join.
SELECT a.x, b.y
FROM t FOR SYSTEM_TIME ALL AS a
JOIN u FOR SYSTEM_TIME AS OF NOW() AS b ON a.id = b.id;

-- Regression: a plain FOR UPDATE clause must still parse.
SELECT * FROM t FOR UPDATE;
