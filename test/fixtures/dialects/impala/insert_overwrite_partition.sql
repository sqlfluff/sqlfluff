INSERT OVERWRITE TABLE target_table PARTITION (partition_code = '202601') SELECT id, name FROM source_table;

INSERT OVERWRITE TABLE target_table SELECT id, name FROM source_table;

WITH src AS (SELECT id, name FROM source_table) INSERT OVERWRITE TABLE target_table PARTITION (partition_code = '202601') SELECT id, name FROM src;

INSERT OVERWRITE TABLE target_table PARTITION (partition_code = '202601') WITH src AS (SELECT id, name FROM source_table) SELECT id, name FROM src;
