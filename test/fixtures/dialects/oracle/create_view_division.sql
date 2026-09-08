CREATE VIEW v1 AS
SELECT 1 / 100 AS z
FROM dual;

CREATE OR REPLACE VIEW v2 AS
SELECT nvl(bytes, 0) / 1024 / 1024 AS size_mb
FROM v$datafile;

CREATE VIEW v3 AS
SELECT a / b AS ratio
FROM t
WHERE sample_time > sysdate - 1 / 24;

create or replace view v4 as
select smthng / 2
from smwhr
/
