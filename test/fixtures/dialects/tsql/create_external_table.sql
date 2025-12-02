CREATE EXTERNAL TABLE schema_name.table_name
(
    column_name_1 VARCHAR(50),
    column_name_2 VARCHAR(50) NULL,
    column_name_3 VARCHAR(50) NOT NULL
)
WITH (
    LOCATION = N'/path/to/folder/',
    DATA_SOURCE = external_data_source,
    FILE_FORMAT = parquetfileformat,
    REJECT_TYPE = VALUE,
    REJECT_VALUE = 0,
    REJECTED_ROW_LOCATION = '/REJECT_Directory'
)

CREATE EXTERNAL TABLE schema_name.table_name
(
    column_name_1 VARCHAR(50),
    column_name_2 VARCHAR(50) NULL,
    column_name_3 VARCHAR(50) NOT NULL
)
WITH (
    LOCATION = N'/path/to/folder/',
    DATA_SOURCE = external_data_source,
    FILE_FORMAT = parquetfileformat,
    REJECT_TYPE = PERCENTAGE,
    REJECT_VALUE = 0,
    REJECT_SAMPLE_VALUE = 0,
    REJECTED_ROW_LOCATION = '/REJECT_DIRECTORY'
)

CREATE EXTERNAL TABLE customers (
    o_orderkey DECIMAL(38) NOT NULL,
    o_custkey DECIMAL(38) NOT NULL,
    o_orderstatus CHAR COLLATE latin1_general_bin NOT NULL,
    o_totalprice DECIMAL(15, 2) NOT NULL,
    o_orderdate DATETIME2(0) NOT NULL,
    o_orderpriority CHAR(15) COLLATE latin1_general_bin NOT NULL,
    o_clerk CHAR(15) COLLATE latin1_general_bin NOT NULL,
    o_shippriority DECIMAL(38) NOT NULL,
    o_comment VARCHAR(79) COLLATE latin1_general_bin NOT NULL
)
WITH (
    LOCATION = 'DB1.mySchema.customer',
    DATA_SOURCE = external_data_source_name
);
