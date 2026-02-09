CREATE TABLE [dbo].[EC DC] (
    [Column B] [varchar](100),
    [ColumnC] varchar(100),
    [ColumnDecimal] decimal(10,3)
)

-- Test various forms of quoted data types
CREATE TABLE foo (
    pk int PRIMARY KEY,
    quoted_name [custom udt],
    qualified_name sch.qualified,
    quoted_qualified "my schema".qualified,
    more_quoted "my schema"."custom udt",
    quoted_udt sch.[custom udt]
);

-- computed column
-- https://learn.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver16#column_name-as-computed_column_expression
-- https://learn.microsoft.com/en-us/sql/relational-databases/tables/specify-computed-columns-in-a-table?view=sql-server-ver16
CREATE TABLE dbo.Products (
    ProductID int IDENTITY (1,1) NOT NULL
    , InventoryTs datetime2(0)
    , QtyAvailable smallint
    , QtySold smallint
    , UnitPrice money
    , InventoryValue1 AS QtyAvailable * UnitPrice PERSISTED
    , InventoryValue2 AS QtyAvailable * UnitPrice PERSISTED NOT NULL
    , InventoryValue3 AS QtyAvailable * UnitPrice
    , InventoryValue4 AS QtyAvailable * UnitPrice PRIMARY KEY
    , [SoldValue] AS (QtySold * UnitPrice)
    , InventoyDate AS CAST(InventoryTs AS date)
);

-- issue #6340
CREATE TABLE [dbo].[Foo](
    [ID] [int] IDENTITY(1,1) NOT NULL
    CONSTRAINT [PK_Foo_ID] PRIMARY KEY CLUSTERED ([ID] ASC),
    [other_ID] [int] FOREIGN KEY REFERENCES [dbo].[Bar] (id) UNIQUE
);

CREATE TABLE dbo.Test(
    ID int NOT NULL primary key,
    name varchar(128) NULL index _name (name)
);
