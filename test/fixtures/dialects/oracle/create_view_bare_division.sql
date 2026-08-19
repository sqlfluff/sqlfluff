-- A bare (unparenthesized) `/` division operator inside a CREATE VIEW ... AS
-- SELECT must parse as division, not as a SQL*Plus slash buffer-executor.
-- https://github.com/sqlfluff/sqlfluff/issues/8373
CREATE VIEW myview AS
SELECT 1 / 100 AS z FROM dual;

CREATE VIEW ratios AS
SELECT nvl(bytes, 0) / 1024 / 1024 AS size_mb
FROM stats
WHERE sample_time > sysdate - 1 / 24;

-- A `/` alone on its own line is still the slash buffer-executor.
CREATE OR REPLACE VIEW example AS
SELECT smthng
FROM smwhr
/
