
CREATE TABLE db_name.table_name
(
    -- Basic types
    `id` UInt64,
    `timestamp` DateTime64(3, 'UTC') CODEC(Delta(8), LZ4),
    `value_raw` Float32,

    -- LowCardinality type
    `category` LowCardinality(String),

    -- Enum type
    `status` Enum8('ACTIVE' = 1, 'INACTIVE' = 2, 'PENDING' = 3),

    -- Nullable type
    `description` Nullable(String),

    -- Array type
    `tags` Array(String),

    -- ALIAS column
    `value_calculated` Float32 ALIAS value_raw / (3600 / 30),
    `flag_active` Int8 ALIAS if(status = 'ACTIVE', 1, 0),
    `value_with_dict` Float32 ALIAS value_raw * dictGetOrDefault('dictionary.lookup', 'key', (category, 'CATEGORY'), toDateTime(timestamp), 0.),

    -- MATERIALIZED column
    `description_is_null` UInt8 MATERIALIZED description IS NULL,

    -- Tuple types
    `coordinates` Tuple(Float64, Float64),
    `named_point` Tuple(x Float64, y Float64, z Float64),

    -- Map type
    `properties` Map(String, String),

    -- JSON type
    `json_data` JSON,

    -- Nested type
    `nested_data` Nested(
        key String,
        value Float64,
        timestamp DateTime
    )
)
ENGINE = MergeTree()
ORDER BY id
SETTINGS index_granularity = 8192;
-- ALTER TABLE examples with various column types and options
ALTER TABLE db_name.table_name ADD COLUMN `new_column` Float32 CODEC(Delta, LZ4);
ALTER TABLE db_name.table_name ADD COLUMN `new_alias_column` Float32 ALIAS value_raw * 2;
ALTER TABLE db_name.table_name ADD COLUMN `new_materialized_column` Float32 MATERIALIZED value_raw * 3;
ALTER TABLE db_name.table_name ADD COLUMN `new_default_column` Float32 DEFAULT 100;
ALTER TABLE db_name.table_name ADD COLUMN `new_enum_column` Enum8('VALUE1' = 1, 'VALUE2' = 2, 'VALUE3' = 3);
ALTER TABLE db_name.table_name ADD COLUMN `new_lowcard_column` LowCardinality(String) DEFAULT 'DEFAULT_VALUE';
ALTER TABLE db_name.table_name ADD COLUMN `new_datetime_column` DateTime64(3, 'UTC') CODEC(Delta(8), LZ4);
ALTER TABLE db_name.table_name ADD COLUMN `new_nullable_column` Nullable(Float32);
ALTER TABLE db_name.table_name ADD COLUMN `new_json_column` JSON;

-- Modify column examples
ALTER TABLE db_name.table_name MODIFY COLUMN `value_raw` Float64 CODEC(Delta, LZ4);
ALTER TABLE db_name.table_name MODIFY COLUMN `value_calculated` Float64 ALIAS value_raw / (3600 / 30);
ALTER TABLE db_name.table_name MODIFY COLUMN `flag_active` Int8 MATERIALIZED if(status = 'ACTIVE', 1, 0);
ALTER TABLE db_name.table_name MODIFY COLUMN `category` LowCardinality(String) DEFAULT 'UNKNOWN_CATEGORY';

-- Remove alias example
ALTER TABLE db_name.table_name MODIFY COLUMN `value_with_dict` REMOVE ALIAS;

-- Drop column example
ALTER TABLE db_name.table_name DROP COLUMN `new_column`;

-- Rename column example
ALTER TABLE db_name.table_name RENAME COLUMN `new_column` TO `new_column_renamed`;

-- Add alias from dictionary
ALTER TABLE db_name.table_name ADD COLUMN `complex_alias` Float32 ALIAS value_raw * dictGetOrDefault('dictionary.lookup', 'price', (category, 'RESOURCE_TYPE'), toDateTime(timestamp), 0.);
