SELECT a.*
   FROM OPENROWSET('Microsoft.Jet.OLEDB.4.0',
                   'C:\SAMPLES\Northwind.mdb';
                   'admin';
                   'password',
                   Customers) AS a;
GO

SELECT d.*
FROM OPENROWSET('SQLNCLI', 'Server=Seattle1;Trusted_Connection=yes;',
                            Department) AS d;
GO

SELECT d.*
FROM OPENROWSET('SQLNCLI', 'Server=Seattle1;Trusted_Connection=yes;',
                 AdventureWorks2012.HumanResources.Department) AS d;
GO

SELECT a.*
FROM OPENROWSET('SQLNCLI', 'Server=Seattle1;Trusted_Connection=yes;',
     'SELECT TOP 10 GroupName, Name
     FROM AdventureWorks2012.HumanResources.Department') AS a;
GO

SELECT * FROM OPENROWSET(
   BULK 'C:\DATA\inv-2017-01-19.csv',
   SINGLE_CLOB) AS DATA;
GO

SELECT *
   FROM OPENROWSET(BULK N'C:\Text1.txt', SINGLE_NCLOB) AS Document;
GO

SELECT *
FROM OPENROWSET(BULK(N'D:\XChange\test-csv.csv',
    N'D:\XChange\test-csv2.csv'),
    FORMATFILE = N'D:\XChange\test-csv.fmt',
    FORMATFILE_DATA_SOURCE = 'root\',
    ROWTERMINATOR = '\n,',
    FIELDTERMINATOR = '\t',
    FIRSTROW=2,
    FORMAT='CSV') AS cars;
GO

SELECT *
FROM OPENROWSET(BULK(
    'https://sqlondemandstorage.blob.core.windows.net/data.csv'
    ),
    FORMAT = 'CSV',
    PARSER_VERSION = '2.0',
    ESCAPE_CHAR = '"',
    HEADER_ROW = TRUE,
    DATAFILETYPE = 'char',
    ROWSET_OPTIONS = '{"READ_OPTIONS":["ALLOW_INCONSISTENT_READS"]}',
    MAXERRORS = 2,
    ERRORFILE_DATA_SOURCE = 'https://sqlondemandstorage.blob.core.windows.net/',
    ERRORFILE_LOCATION = 'path\to\errorfile.csv'
)

SELECT *
FROM OPENROWSET(BULK(
    N'https://azureopendatastorage.blob.core.windows.net/censusdatacontainer/',
    'file_does_not_exist.parquet'
    ),
    FORMAT='PARQUET',
    LASTROW = 10000,
    ROWS_PER_BATCH = 1000
) AS name;

SELECT TOP 10 *
from OPENROWSET(BULK 'https://pandemicdatalake.blob.core.windows.net/public/curated/covid-19/ecdc_cases/latest/ecdc_cases.parquet',
    DATA_SOURCE = 'MyAzureBlobStorage',
    FORMAT = 'PARQUET') as rows
GO

SELECT TOP 10 *
FROM OPENROWSET(
      BULK 'https://pandemicdatalake.blob.core.windows.net/public/curated/covid-19/ecdc_cases/latest/ecdc_cases.parquet',
      FORMAT = 'PARQUET'
   )
WITH (
    [country_code] VARCHAR(5) COLLATE Latin1_General_BIN2,
    [country_name] VARCHAR(100) COLLATE Latin1_General_BIN2 2,
    [year] smallint,
    [population] bigint
) as rows
GO

SELECT
    TOP 1 *
FROM OPENROWSET(
        BULK 'https://azureopendatastorage.blob.core.windows.net/censusdatacontainer/release/us_population_county/year=20*/*.parquet',
        FORMAT='PARQUET'
    )
WITH (
    [stateName] VARCHAR(50),
    [stateName_explicit_path] VARCHAR(50) '$.stateName',
    [COUNTYNAME] VARCHAR(50),
    [countyName_explicit_path] VARCHAR(50) '$.COUNTYNAME',
    [population] bigint 'strict $.population'
)
AS [r]
GO
