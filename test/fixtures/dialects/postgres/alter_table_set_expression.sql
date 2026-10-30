-- SET EXPRESSION was added in PostgreSQL 17 to modify generated column expressions.
-- https://www.postgresql.org/docs/17/sql-altertable.html

ALTER TABLE message_events
ALTER COLUMN guild_id
SET EXPRESSION AS ((raw_data ->> 'guild_id')::BIGINT);

ALTER TABLE message_events
ALTER COLUMN guild_id
SET EXPRESSION AS (COALESCE((additional_data #>> '{guild_id}')::BIGINT, (raw_data ->> 'guild_id')::BIGINT));
