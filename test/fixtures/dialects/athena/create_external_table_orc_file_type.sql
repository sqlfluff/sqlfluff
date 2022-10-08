CREATE EXTERNAL TABLE my_table(
  col_1 string,
  col_2 boolean,
  col_3 bigint,
  col_4 string,
  col_5 string
  )
  PARTITIONED BY (field_partition string)
  ROW FORMAT SERDE 'org.apache.hadoop.hive.ql.io.orc.OrcSerde'
  STORED AS INPUTFORMAT 'org.apache.hadoop.hive.ql.io.SymlinkTextInputFormat'
  OUTPUTFORMAT  'org.apache.hadoop.hive.ql.io.IgnoreKeyTextOutputFormat'
  LOCATION 's3://athena-examples-myregion/flight/orc_data/'
  TBLPROPERTIES ('has_encrypted_data'='true');