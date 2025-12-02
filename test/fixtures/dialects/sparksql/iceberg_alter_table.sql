-- Iceberg Spark DDL Alter Statements https://iceberg.apache.org/docs/latest/spark-ddl/#alter-table

ALTER TABLE prod.db.sample RENAME TO prod.db.new_name;

ALTER TABLE prod.db.sample SET TBLPROPERTIES (
    'read.split.target-size'='268435456'
);

ALTER TABLE prod.db.sample UNSET TBLPROPERTIES ('read.split.target-size');

ALTER TABLE prod.db.sample SET TBLPROPERTIES (
    'comment' = 'A table comment.'
);

ALTER TABLE prod.db.sample
ADD COLUMNS (
    new_column string comment 'new_column docs'
  );

-- create a struct column
ALTER TABLE prod.db.sample
ADD COLUMN point struct<x: double, y: double>;

-- add a field to the struct
ALTER TABLE prod.db.sample
ADD COLUMN point.z double;

-- create a nested array column of struct
ALTER TABLE prod.db.sample
ADD COLUMN points array<struct<x: double, y: double>>;

-- add a field to the struct within an array. Using keyword 'element' to access the array's element column.
ALTER TABLE prod.db.sample
ADD COLUMN points.element.z double;

-- create a map column of struct key and struct value
ALTER TABLE prod.db.sample
ADD COLUMN points map<struct<x: int>, struct<a: int>>;

-- add a field to the value struct in a map. Using keyword 'value' to access the map's value column.
ALTER TABLE prod.db.sample
ADD COLUMN points.value.b int;

ALTER TABLE prod.db.sample
ADD COLUMN new_column bigint AFTER other_column;

ALTER TABLE prod.db.sample
ADD COLUMN nested.new_column bigint FIRST;

ALTER TABLE prod.db.sample RENAME COLUMN data TO payload;

ALTER TABLE prod.db.sample RENAME COLUMN location.lat TO latitude;

ALTER TABLE prod.db.sample ALTER COLUMN measurement TYPE double;

ALTER TABLE prod.db.sample ALTER COLUMN measurement TYPE double COMMENT 'unit is bytes per second';

ALTER TABLE prod.db.sample ALTER COLUMN measurement COMMENT 'unit is kilobytes per second';

ALTER TABLE prod.db.sample ALTER COLUMN col FIRST;

ALTER TABLE prod.db.sample ALTER COLUMN nested.col AFTER other_col;

ALTER TABLE prod.db.sample ALTER COLUMN id DROP NOT NULL;

ALTER TABLE prod.db.sample DROP COLUMN id;

ALTER TABLE prod.db.sample DROP COLUMN point.z;

ALTER TABLE prod.db.sample ADD PARTITION FIELD catalog; -- identity transform

ALTER TABLE prod.db.sample ADD PARTITION FIELD bucket(16, id);

ALTER TABLE prod.db.sample ADD PARTITION FIELD truncate(4, data);

ALTER TABLE prod.db.sample ADD PARTITION FIELD years(ts);

-- use optional AS keyword to specify a custom name for the partition field
ALTER TABLE prod.db.sample ADD PARTITION FIELD bucket(16, id) AS shard;

ALTER TABLE prod.db.sample DROP PARTITION FIELD catalog;

ALTER TABLE prod.db.sample DROP PARTITION FIELD bucket(16, id);

ALTER TABLE prod.db.sample DROP PARTITION FIELD truncate(4, data);

ALTER TABLE prod.db.sample DROP PARTITION FIELD years(ts);

ALTER TABLE prod.db.sample DROP PARTITION FIELD shard;

ALTER TABLE prod.db.sample REPLACE PARTITION FIELD ts_day WITH days(ts);

-- use optional AS keyword to specify a custom name for the new partition field
ALTER TABLE prod.db.sample REPLACE PARTITION FIELD ts_day WITH days(ts) AS day_of_ts;

ALTER TABLE prod.db.sample WRITE ORDERED BY category, id;

-- use optional ASC/DEC keyword to specify sort order of each field (default ASC)
ALTER TABLE prod.db.sample WRITE ORDERED BY category ASC, id DESC;

-- use optional NULLS FIRST/NULLS LAST keyword to specify null order of each field (default FIRST)
ALTER TABLE prod.db.sample WRITE ORDERED BY category ASC NULLS LAST, id DESC NULLS FIRST;

ALTER TABLE prod.db.sample WRITE LOCALLY ORDERED BY category, id;

ALTER TABLE prod.db.sample WRITE DISTRIBUTED BY PARTITION;

ALTER TABLE prod.db.sample WRITE DISTRIBUTED BY PARTITION LOCALLY ORDERED BY category, id;

-- single column
ALTER TABLE prod.db.sample SET IDENTIFIER FIELDS id;

-- multiple columns
ALTER TABLE prod.db.sample SET IDENTIFIER FIELDS id, data;

-- single column
ALTER TABLE prod.db.sample DROP IDENTIFIER FIELDS id;

-- multiple columns
ALTER TABLE prod.db.sample DROP IDENTIFIER FIELDS id, data
