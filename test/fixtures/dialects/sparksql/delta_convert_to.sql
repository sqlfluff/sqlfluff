-- Convert unpartitioned Parquet table at path '<path-to-table>'
CONVERT TO DELTA PARQUET.`/data/events/`;

-- Convert partitioned Parquet table at path '<path-to-table>'
-- and partitioned by integer columns named 'part' and 'part2'
CONVERT TO DELTA PARQUET.`/data/events/` PARTITIONED BY (part int, part2 int);

-- Convert the Iceberg table in the path <path-to-table>.
CONVERT TO DELTA ICEBERG.`/data/events/`;

-- Convert the Iceberg table in the path <path-to-table>
-- without collecting statistics
CONVERT TO DELTA ICEBERG.`/data/events/` NO STATISTICS;

-- table_name is "either an optionally qualified table identifier or a path".
-- https://docs.databricks.com/aws/en/sql/language-manual/delta-convert-to-delta
CONVERT TO DELTA events;

CONVERT TO DELTA main.default.events;

CONVERT TO DELTA events NO STATISTICS;

CONVERT TO DELTA events PARTITIONED BY (part int, part2 int);
