-- MariaDB supports IF [NOT] EXISTS on CREATE/ALTER/DROP SEQUENCE, and a
-- comma-separated name list on DROP SEQUENCE. ANSI/MySQL do not.
-- https://mariadb.com/kb/en/create-sequence/
-- https://mariadb.com/kb/en/alter-sequence/
-- https://mariadb.com/kb/en/drop-sequence/

-- CREATE SEQUENCE [IF NOT EXISTS]
CREATE SEQUENCE IF NOT EXISTS `s1`;
CREATE SEQUENCE IF NOT EXISTS s2 START WITH 100 INCREMENT BY 10;

-- ALTER SEQUENCE [IF EXISTS]
ALTER SEQUENCE IF EXISTS `s1` INCREMENT BY 5;

-- DROP SEQUENCE [IF EXISTS] name[, name ...]
DROP SEQUENCE IF EXISTS `s1`;
DROP SEQUENCE IF EXISTS s1, s2, s3;

-- Regression: the clauses are optional; bare forms and the DROP list are
-- unchanged.
CREATE SEQUENCE `s1`;
ALTER SEQUENCE `s1` INCREMENT BY 5;
DROP SEQUENCE `s1`;
DROP SEQUENCE s1, s2;
