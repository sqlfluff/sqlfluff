-- System-versioned tables.
-- https://mariadb.com/kb/en/system-versioned-tables/

-- Simplified form: the period columns are implicit.
CREATE TABLE t (
   x INT
) WITH SYSTEM VERSIONING;

-- Explicit form: named ROW START / ROW END columns and PERIOD FOR SYSTEM_TIME.
CREATE TABLE t_explicit (
   x INT,
   start_timestamp TIMESTAMP(6) GENERATED ALWAYS AS ROW START,
   end_timestamp TIMESTAMP(6) GENERATED ALWAYS AS ROW END,
   PERIOD FOR SYSTEM_TIME(start_timestamp, end_timestamp)
) WITH SYSTEM VERSIONING;
