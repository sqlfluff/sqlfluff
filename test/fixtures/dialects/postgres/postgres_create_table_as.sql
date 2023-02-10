CREATE TEMP TABLE t1 AS (
    SELECT something
    FROM t2
);

CREATE TEMP TABLE t1 AS
    SELECT something
    FROM t2
;

CREATE TEMPORARY TABLE t1 AS
    SELECT something
    FROM t2
;

CREATE TABLE t1 AS (
    SELECT something
    FROM t2
);

CREATE TABLE t1 AS
    SELECT something
    FROM t2
;

CREATE TABLE IF NOT EXISTS t1 AS
    SELECT something
    FROM t2
;

CREATE TABLE t1 ON COMMIT DELETE ROWS AS
    SELECT something
    FROM t2
;

CREATE TABLE t1 ON COMMIT PRESERVE ROWS AS
    SELECT something
    FROM t2
;

CREATE TABLE t1 ON COMMIT DROP AS
    SELECT something
    FROM t2
;

CREATE TABLE t1 AS (
    SELECT something
    FROM t2
)
WITH NO DATA
;

CREATE TABLE t1 AS
SELECT something
FROM t2
WITH NO DATA
;

CREATE TABLE t1 AS (
    SELECT something
    FROM t2
)
WITH DATA
;

CREATE TABLE t1 AS
SELECT something
FROM t2
WITH DATA
;

CREATE UNLOGGED TABLE t1 AS
    SELECT something
    FROM t2
;

CREATE GLOBAL TEMP TABLE t1 AS
    SELECT something
    FROM t2
;

CREATE LOCAL TEMP TABLE t1 AS
    SELECT something
    FROM t2
;

CREATE TABLE t1 USING method AS
    SELECT something
    FROM t2
;

CREATE TABLE t1 WITHOUT OIDS AS
    SELECT something
    FROM t2
;

CREATE TABLE t1 (c1, c2, c3) AS VALUES
    ('val1', 'val2', 'val3'),
    ('val4', 'val5', 'val6')
;

CREATE TABLE t1 AS
    TABLE t2
;

CREATE TABLE t1 AS
    EXECUTE func()
;

CREATE TABLE t1 TABLESPACE ts AS
    SELECT something
    FROM t2
;

CREATE TABLE t1 WITH (val=70) AS
    SELECT something
    FROM t2
;

create temp table t1
with (autovacuum_enabled = true, toast_tuple_target = 123, vacuum_index_cleanup = false) as
select
    column_1
    , column_2
    , column_3
from tablename;

create temp table a_new_table
with (appendoptimized = true, compresstype = zstd) as
select
    column_1
    , column_2
    , column_3
from schema.tablename
group by 1, 2, 3;
