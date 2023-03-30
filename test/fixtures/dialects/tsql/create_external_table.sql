CREATE EXTERNAL TABLE schema_name.table_name
(
    column_name_1 VARCHAR(50),
    column_name_2 VARCHAR(50) NULL,
    column_name_3 VARCHAR(50) NOT NULL
)
WITH (
    DATA_SOURCE = external_data_source
)
