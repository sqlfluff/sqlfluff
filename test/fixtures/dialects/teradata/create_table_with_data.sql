CREATE VOLATILE TABLE a AS (SELECT 'A' AS B) WITH DATA ON COMMIT PRESERVE ROWS;

CREATE VOLATILE TABLE b AS (SELECT 'A' AS B) WITH DATA ON COMMIT DELETE ROWS;

CREATE VOLATILE TABLE c AS (SELECT 'A' AS B) WITH NO DATA;
