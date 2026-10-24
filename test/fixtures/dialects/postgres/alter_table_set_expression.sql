-- SET EXPRESSION was added in PostgreSQL 17 to modify generated column expressions.
-- https://www.postgresql.org/docs/17/sql-altertable.html

ALTER TABLE message_events
ALTER COLUMN guild_id
SET EXPRESSION AS ((raw_data ->> 'guild_id')::BIGINT);

ALTER TABLE message_events
ALTER COLUMN guild_id
SET EXPRESSION AS (COALESCE((additional_data #>> '{guild_id}')::BIGINT, (raw_data ->> 'guild_id')::BIGINT));

ALTER TABLE measurements ALTER generated_value SET EXPRESSION AS (base_value + 1);

ALTER TABLE public.measurements
ALTER COLUMN generated_value SET EXPRESSION AS (COALESCE(ABS(base_value), 0));

ALTER TABLE "measurements"
ALTER COLUMN "generated value" SET EXPRESSION AS ("base value" * 2);

ALTER TABLE measurements
ALTER COLUMN generated_value SET EXPRESSION AS (base_value + 2),
ALTER COLUMN generated_value SET NOT NULL;

ALTER TABLE IF EXISTS ONLY measurements
ALTER COLUMN generated_value SET EXPRESSION AS (
    CASE WHEN base_value > 0 THEN base_value ELSE 0 END
);
