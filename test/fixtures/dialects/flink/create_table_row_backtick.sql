CREATE TABLE mytopic (
    `metadata1` ROW<`key` STRING, `value` STRING, `unit` STRING>,
    `metadata2` ARRAY<ROW<`key` STRING, `value` STRING, `unit` STRING>>
) WITH (
    'topic' = 'mytopic'
);

CREATE TABLE t (
    col ROW<key STRING, value STRING>
);

CREATE TABLE t (
    col ROW<`field_name` INT, `another_field` BIGINT>
);