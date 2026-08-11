-- Purging history rows from system-versioned tables with DELETE HISTORY.
-- https://mariadb.com/kb/en/delete/

-- Delete all history.
DELETE HISTORY FROM t;

-- Delete history before a point in time.
DELETE HISTORY FROM t BEFORE SYSTEM_TIME '2020-01-01 00:00:00';

-- The optional TIMESTAMP / TRANSACTION qualifier.
DELETE HISTORY FROM t BEFORE SYSTEM_TIME TIMESTAMP '2020-01-01 00:00:00';
DELETE HISTORY FROM t BEFORE SYSTEM_TIME TRANSACTION 10;

-- Restrict to given partitions.
DELETE HISTORY FROM t PARTITION (p0, p1) BEFORE SYSTEM_TIME NOW();

-- Regression: ordinary DELETE forms must still parse unchanged.
DELETE FROM t WHERE a = 1;
DELETE FROM t FOR PORTION OF date_period FROM '2001-01-01' TO '2018-01-01';
