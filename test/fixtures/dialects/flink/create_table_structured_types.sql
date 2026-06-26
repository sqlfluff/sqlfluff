CREATE TABLE mytopic (
    `metadata1` ROW<`key` STRING, `value` STRING, `unit` STRING>,
    `metadata2` ARRAY <ROW<`key` STRING, `value` STRING, `unit` STRING>>
) WITH (
    'topic' = 'mytopic'
);
