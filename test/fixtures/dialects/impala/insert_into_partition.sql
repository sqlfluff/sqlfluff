INSERT INTO TABLE target_table PARTITION (partition_code) SELECT id, name, partition_code FROM source_table;

INSERT INTO TABLE target_table SELECT id, name FROM source_table;
