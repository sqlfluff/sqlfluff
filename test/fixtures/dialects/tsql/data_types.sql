-- Test file for T-SQL data types
-- https://learn.microsoft.com/en-us/sql/t-sql/data-types/data-types-transact-sql

-- Exact numeric types (no parameters)
DECLARE @tinyint_var TINYINT;
DECLARE @smallint_var SMALLINT;
DECLARE @int_var INT;
DECLARE @bigint_var BIGINT;
DECLARE @bit_var BIT;
DECLARE @money_var MONEY;
DECLARE @smallmoney_var SMALLMONEY;

-- Exact numeric types (with precision and scale)
DECLARE @decimal_var DECIMAL;
DECLARE @decimal_p_var DECIMAL(10);
DECLARE @decimal_ps_var DECIMAL(10, 2);
DECLARE @numeric_var NUMERIC;
DECLARE @numeric_p_var NUMERIC(18);
DECLARE @numeric_ps_var NUMERIC(18, 4);
DECLARE @dec_var DEC;
DECLARE @dec_p_var DEC(15);
DECLARE @dec_ps_var DEC(15, 3);

-- Approximate numeric types
DECLARE @float_var FLOAT;
DECLARE @float_p_var FLOAT(24);
DECLARE @real_var REAL;

-- Date and time types
DECLARE @date_var DATE;
DECLARE @smalldatetime_var SMALLDATETIME;
DECLARE @datetime_var DATETIME;
DECLARE @time_var TIME;
DECLARE @time_p_var TIME(7);
DECLARE @datetime2_var DATETIME2;
DECLARE @datetime2_p_var DATETIME2(7);
DECLARE @datetimeoffset_var DATETIMEOFFSET;
DECLARE @datetimeoffset_p_var DATETIMEOFFSET(7);

-- Character string types
DECLARE @char_var CHAR;
DECLARE @char_n_var CHAR(10);
DECLARE @character_var CHARACTER;
DECLARE @character_n_var CHARACTER(10);
DECLARE @char_varying_var CHAR VARYING;
DECLARE @char_varying_n_var CHAR VARYING(100);
DECLARE @character_varying_var CHARACTER VARYING;
DECLARE @character_varying_n_var CHARACTER VARYING(100);
DECLARE @varchar_var VARCHAR;
DECLARE @varchar_n_var VARCHAR(50);
DECLARE @varchar_max_var VARCHAR(MAX);
DECLARE @text_var TEXT;

-- Unicode character string types
DECLARE @nchar_var NCHAR;
DECLARE @nchar_n_var NCHAR(10);
-- DECLARE @national_char_var NATIONAL CHAR;
DECLARE @national_char_n_var NATIONAL CHAR(10);
DECLARE @national_character_var NATIONAL CHARACTER;
DECLARE @national_character_n_var NATIONAL CHARACTER(10);
DECLARE @nchar_varying_var NCHAR VARYING;
DECLARE @nchar_varying_n_var NCHAR VARYING(100);
DECLARE @nvarchar_var NVARCHAR;
DECLARE @nvarchar_n_var NVARCHAR(50);
DECLARE @nvarchar_max_var NVARCHAR(MAX);
DECLARE @national_char_varying_var NATIONAL CHARACTER VARYING;
DECLARE @national_char_varying_n_var NATIONAL CHARACTER VARYING(100);
DECLARE @ntext_var NTEXT;

-- Binary string types
DECLARE @binary_var BINARY;
DECLARE @binary_n_var BINARY(10);
DECLARE @varbinary_var VARBINARY;
DECLARE @varbinary_n_var VARBINARY(50);
DECLARE @varbinary_max_var VARBINARY(MAX);
DECLARE @image_var IMAGE;

-- Other data types
DECLARE @cursor_var CURSOR;
DECLARE @sql_variant_var SQL_VARIANT;
DECLARE @timestamp_var TIMESTAMP;
DECLARE @rowversion_var ROWVERSION;
DECLARE @uniqueidentifier_var UNIQUEIDENTIFIER;
DECLARE @xml_var XML;
DECLARE @json_var JSON;

-- Spatial types
DECLARE @geography_var GEOGRAPHY;
DECLARE @geometry_var GEOMETRY;
DECLARE @hierarchyid_var HIERARCHYID;

-- Vector type (Azure SQL Database)
DECLARE @vector_var VECTOR;
DECLARE @vector_n_var VECTOR(1536);

-- User-defined data types
DECLARE @custom_type MyCustomType;

-- Schema-qualified data types
DECLARE @sys_type sys.sysname;

-- Bracketed data type identifiers
DECLARE @bracketed_type [sys].[sysname];
GO

-- Data types in CREATE TABLE
CREATE TABLE DataTypesTest (
    -- Exact numeric
    col_tinyint TINYINT,
    col_smallint SMALLINT,
    col_int INT,
    col_bigint BIGINT,
    col_bit BIT,
    col_money MONEY,
    col_smallmoney SMALLMONEY,
    col_decimal DECIMAL(18, 2),
    col_numeric NUMERIC(10, 5),

    -- Approximate numeric
    col_float FLOAT,
    col_real REAL,

    -- Date and time
    col_date DATE,
    col_time TIME(7),
    col_datetime DATETIME,
    col_datetime2 DATETIME2(7),
    col_datetimeoffset DATETIMEOFFSET(7),
    col_smalldatetime SMALLDATETIME,

    -- Character strings
    col_char CHAR(10),
    col_varchar VARCHAR(50),
    col_varchar_max VARCHAR(MAX),
    col_text TEXT,

    -- Unicode strings
    col_nchar NCHAR(10),
    col_nvarchar NVARCHAR(100),
    col_nvarchar_max NVARCHAR(MAX),
    col_ntext NTEXT,

    -- Binary strings
    col_binary BINARY(10),
    col_varbinary VARBINARY(100),
    col_varbinary_max VARBINARY(MAX),
    col_image IMAGE,

    -- Other types
    col_uniqueidentifier UNIQUEIDENTIFIER,
    col_xml XML,
    col_json JSON,
    col_geography GEOGRAPHY,
    col_geometry GEOMETRY,
    col_hierarchyid HIERARCHYID,
    col_sql_variant SQL_VARIANT,
    col_timestamp TIMESTAMP,
    col_rowversion ROWVERSION
);
GO

-- Function parameters with data types
CREATE FUNCTION TestDataTypes(
    @param_int INT,
    @param_varchar VARCHAR(100),
    @param_decimal DECIMAL(10, 2),
    @param_datetime DATETIME2,
    @param_nvarchar NVARCHAR(MAX)
)
RETURNS INT
AS
BEGIN
    RETURN 1;
END;
GO

-- Procedure parameters with data types
CREATE PROCEDURE TestDataTypesProc
    @param_bigint BIGINT,
    @param_nchar NCHAR(50),
    @param_varbinary VARBINARY(MAX),
    @param_xml XML,
    @param_geography GEOGRAPHY
AS
BEGIN
    SELECT @param_bigint;
END;
