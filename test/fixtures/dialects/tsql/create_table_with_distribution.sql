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
--Azure Synapse Analytics specific
CREATE TABLE [dbo].[EC DC] (
    [Column B] [varchar](100),
    [ColumnC] varchar(100),
    [ColumnDecimal] decimal(10,3)
)
WITH (HEAP, DISTRIBUTION = REPLICATE);
GO
DROP TABLE [dbo].[EC DC]
GO
--Azure Synapse Analytics specific
CREATE TABLE [dbo].[EC DC] (
    [Column B] [varchar](100),
    [ColumnC] varchar(100),
    [ColumnDecimal] decimal(10,3)
)
WITH (LOCATION = USER_DB, DISTRIBUTION = HASH([Column B]));
GO
DROP TABLE [dbo].[EC DC]
GO
