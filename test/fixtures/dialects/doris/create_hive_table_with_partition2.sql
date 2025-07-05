CREATE TABLE partition_table (
  `col1` BOOLEAN COMMENT 'col1',
  `col2` INT COMMENT 'col2',
  `col3` BIGINT COMMENT 'col3',
  `col4` DECIMAL(2,1) COMMENT 'col4',
  `pt1` VARCHAR COMMENT 'pt1',
  `pt2` VARCHAR COMMENT 'pt2'
)  ENGINE=hive
PARTITION BY LIST (pt1, pt2) ()
PROPERTIES (
  'file_format'='orc',
  'compression'='zlib'
);
