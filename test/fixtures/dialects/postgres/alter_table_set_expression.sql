-- "SET EXPRESSION AS" was added in PostgreSQL 18.
-- https://www.postgresql.org/docs/18/sql-altertable.html

ALTER TABLE message_events
ALTER COLUMN guild_id
SET EXPRESSION AS ((raw_data ->> 'guild_id')::BIGINT);

ALTER TABLE message_events
ALTER guild_id
SET EXPRESSION AS (COALESCE((additional_data #>> '{guild_id}')::BIGINT, (raw_data ->> 'guild_id')::BIGINT));
