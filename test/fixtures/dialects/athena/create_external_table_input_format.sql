CREATE EXTERNAL TABLE my_table(
    col_1 string,
    col_2 boolean,
    col_3 bigint,
    col_4 string,
    col_5 string
)
PARTITIONED BY (field_partition string)
ROW FORMAT SERDE 'some row format'
STORED AS INPUTFORMAT 'some input format'
OUTPUTFORMAT 'some output format'
LOCATION 's3://athena-examples-myregion/some_data/'
TBLPROPERTIES ('has_encrypted_data' = 'true');
