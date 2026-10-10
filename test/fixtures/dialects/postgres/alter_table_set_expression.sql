ALTER TABLE message_events
ALTER COLUMN guild_id
SET EXPRESSION AS ((raw_data ->> 'guild_id')::BIGINT);

ALTER TABLE message_events
ALTER COLUMN guild_id
SET EXPRESSION AS (
    COALESCE(
        (additional_data #>> '{guild_id}')::BIGINT,
        (raw_data ->> 'guild_id')::BIGINT
    )
);

ALTER TABLE measurements ALTER area SET EXPRESSION AS (width * height);

ALTER TABLE IF EXISTS ONLY public."Measurements"
ALTER COLUMN "Area" SET EXPRESSION AS ("Width" * "Height");

ALTER TABLE measurements
ALTER COLUMN area SET EXPRESSION AS (width * height),
ALTER COLUMN perimeter SET EXPRESSION AS (2 * (width + height)),
ALTER COLUMN volume DROP EXPRESSION IF EXISTS;
