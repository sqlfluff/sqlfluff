create external table my_database.my_table(
    field_1 string,
    field_2 int,
    field_3 float
)  PARTITIONED BY (field_partition string)
    STORED AS ORC
    tblproperties ("orc.compress"="ZLIB")
    LOCATION 's3://athena-examples-myregion/flight/csv/';
