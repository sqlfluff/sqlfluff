-- Basic CREATE EXTERNAL TABLE using Parquet
CREATE EXTERNAL TABLE populationExternalTable
(
    [country_code] VARCHAR(5) COLLATE Latin1_General_BIN2,
    [country_name] VARCHAR(100) COLLATE Latin1_General_BIN2,
    [year] SMALLINT,
    [population] BIGINT
)
WITH (
    LOCATION = 'csv/population/population.csv',
    DATA_SOURCE = sqlondemanddemo,
    FILE_FORMAT = QuotedCSVWithHeaderFormat
);

-- CREATE EXTERNAL TABLE using Parquet on a set of wildcard files
CREATE EXTERNAL TABLE Taxi
(
    vendor_id VARCHAR(100) COLLATE Latin1_General_BIN2,
    pickup_datetime DATETIME2,
    dropoff_datetime DATETIME2,
    passenger_count INT,
    trip_distance FLOAT,
    fare_amount FLOAT,
    tip_amount FLOAT,
    tolls_amount FLOAT,
    total_amount FLOAT
)
WITH (
    LOCATION = 'yellow/puYear=*/puMonth=*/*.parquet',
    DATA_SOURCE = nyctlc,
    FILE_FORMAT = ParquetFormat
);

-- CREATE EXTERNAL TABLE with TABLE_OPTIONS for appendable files
CREATE EXTERNAL TABLE populationAppendable
(
    [country_code] VARCHAR(5) COLLATE Latin1_General_BIN2,
    [country_name] VARCHAR(100) COLLATE Latin1_General_BIN2,
    [year] SMALLINT,
    [population] BIGINT
)
WITH (
    LOCATION = 'csv/population/population.csv',
    DATA_SOURCE = sqlondemanddemo,
    FILE_FORMAT = QuotedCSVWithHeaderFormat,
    TABLE_OPTIONS = N'{"READ_OPTIONS":["ALLOW_INCONSISTENT_READS"]}'
);

-- CREATE EXTERNAL TABLE on a Delta Lake folder
CREATE EXTERNAL TABLE Covid
(
    date_rep DATE,
    cases INT,
    geo_id VARCHAR(6)
)
WITH (
    LOCATION = 'covid',
    DATA_SOURCE = DeltaLakeStorage,
    FILE_FORMAT = DeltaLakeFormat
);

-- CREATE EXTERNAL TABLE with reject options
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
);
