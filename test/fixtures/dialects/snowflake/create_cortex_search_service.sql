-- create cortex search service my_service;

CREATE OR REPLACE CORTEX SEARCH SERVICE mysvc
  ON transcript_text
  ATTRIBUTES region,agent_id
  WAREHOUSE = mywh
  TARGET_LAG = '1 hour'
  EMBEDDING_MODEL = 'snowflake-arctic-embed-l-v2.0'
AS (
  SELECT
      transcript_text,
      date,
      region,
      agent_id
  FROM support_db.public.transcripts_etl
);

create cortex search service my_service
on text
attributes id, type, title
warehouse = my_warehouse
target_lag = '1 days'
as
select text, id, type, title,
from my_db.my_schema.my_table
;

create or replace cortex search service my_service
on text
warehouse = my_warehouse
target_lag = '1 days'
as
select text, id, type, title,
from my_db.my_schema.my_table
;
