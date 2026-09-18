-- PRIVATE streaming tables: visible inside the pipeline, not published to
-- the catalog.
CREATE OR REFRESH PRIVATE STREAMING TABLE st_private (a BIGINT);

CREATE PRIVATE STREAMING TABLE st_private_2 (a BIGINT);

CREATE OR REFRESH PRIVATE STREAMING TABLE st_private_3
AS SELECT * FROM STREAM read_files('/Volumes/main/landing/events');

-- Still parse, unchanged.
CREATE OR REFRESH STREAMING TABLE st_public (a BIGINT);

CREATE OR REFRESH PRIVATE MATERIALIZED VIEW mv_private AS SELECT 1 AS a;

-- CREATE FLOW: the AUTO CDC branch, with and without ONCE, and with a
-- comment.
CREATE FLOW cdc_flow AS AUTO CDC INTO target
FROM STREAM source
KEYS (id)
SEQUENCE BY sequence_num;

CREATE FLOW cdc_flow_once AS AUTO CDC ONCE INTO target
FROM STREAM source
KEYS (id)
SEQUENCE BY sequence_num;

CREATE FLOW cdc_flow_comment
COMMENT 'Backfill the target once from the archive.'
AS AUTO CDC ONCE INTO target
FROM STREAM source
KEYS (id)
SEQUENCE BY sequence_num;

-- CREATE FLOW: the append branch. This is how a pipeline points several
-- sources at one streaming table.
CREATE FLOW append_flow AS INSERT INTO target BY NAME
SELECT * FROM STREAM source_a;

-- Both documented spellings of ONCE.
CREATE FLOW append_flow_once AS INSERT ONCE INTO target BY NAME
SELECT * FROM STREAM archive;

CREATE FLOW append_flow_into_once AS INSERT INTO ONCE target BY NAME
SELECT * FROM STREAM archive;

CREATE FLOW append_flow_comment
COMMENT 'Backfill historical data.'
AS INSERT ONCE INTO target BY NAME
SELECT * FROM archive_2024;

CREATE FLOW append_flow_replace_using AS INSERT INTO target BY NAME
REPLACE USING (event_date)
SELECT * FROM STREAM source_b;
