--Azure Synapse Analytics specific
CREATE TABLE [dbo].[EC DC] (
    [Column B] [varchar](100),
    [ColumnC] varchar(100),
    [ColumnDecimal] decimal(10,3)
)
WITH (CLUSTERED COLUMNSTORE INDEX, DISTRIBUTION = ROUND_ROBIN);
GO
DROP TABLE [dbo].[EC DC]
GO

CREATE TABLE [dbo].[EC DC] (
    [Column B] [varchar](100),
    [ColumnC] varchar(100),
    [ColumnDecimal] decimal(10,3)
)
WITH (HEAP, DISTRIBUTION = REPLICATE);
GO
DROP TABLE [dbo].[EC DC]
GO

CREATE TABLE [dbo].[EC DC] (
    [Column B] [varchar](100),
    [ColumnC] varchar(100),
    [ColumnDecimal] decimal(10,3)
)
WITH (LOCATION = USER_DB, DISTRIBUTION = HASH([Column B]));
GO
DROP TABLE [dbo].[EC DC]
GO

CREATE TABLE [dbo].[EC DC] (
    [Column B] [varchar](100),
    [ColumnC] varchar(100),
    [ColumnDecimal] decimal(10,3)
)
WITH (CLUSTERED COLUMNSTORE INDEX, LOCATION = USER_DB, DISTRIBUTION = HASH([Column B]));
GO
DROP TABLE [dbo].[EC DC]
GO

CREATE TABLE [dbo].[EC DC] (
    [Column B] [varchar](100),
    [ColumnC] varchar(100),
    [ColumnDecimal] decimal(10,3)
)
WITH (CLUSTERED INDEX ([Column B]), DISTRIBUTION = HASH([Column B]));
GO
DROP TABLE [dbo].[EC DC];
GO


CREATE TABLE [dbo].[EC DC] (
    [Column B] [varchar](100),
    [ColumnC] varchar(100),
    [ColumnDecimal] decimal(10,3)
)
WITH (CLUSTERED COLUMNSTORE INDEX ORDER ([Column B]), DISTRIBUTION = HASH([Column B]));
GO
DROP TABLE [dbo].[EC DC];
GO

CREATE TABLE [dbo].[table] ( [name] [varchar](100) NOT NULL, [month_num] [int] NULL )
WITH ( DISTRIBUTION = REPLICATE, CLUSTERED INDEX ( [name] ASC, [month_num] ASC ) )
GO
