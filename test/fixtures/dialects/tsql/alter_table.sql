CREATE TABLE dbo.doc_exa (column_a INT) ;
GO
ALTER TABLE dbo.doc_exa ADD column_b VARCHAR(20) NULL ;
GO

CREATE TABLE dbo.doc_exc (column_a INT) ;
GO
ALTER TABLE dbo.doc_exc ADD column_b VARCHAR(20) NULL
    CONSTRAINT exb_unique UNIQUE, DROP COLUMN column_a, DROP COLUMN IF EXISTS column_c ;
GO
EXEC sp_help doc_exc ;
GO
DROP TABLE dbo.doc_exc ;
GO


CREATE TABLE dbo.doc_exz (column_a INT, column_b INT) ;
GO
INSERT INTO dbo.doc_exz (column_a) VALUES (7) ;
GO
ALTER TABLE dbo.doc_exz
  ADD CONSTRAINT col_b_def
  DEFAULT 50 FOR column_b ;
GO
INSERT INTO dbo.doc_exz (column_a) VALUES (10) ;
GO
SELECT * FROM dbo.doc_exz ;
GO
DROP TABLE dbo.doc_exz ;
GO


ALTER TABLE Production.TransactionHistoryArchive
ADD CONSTRAINT PK_TransactionHistoryArchive_TransactionID PRIMARY KEY CLUSTERED (TransactionID)
GO

ALTER TABLE Production.TransactionHistoryArchive
ALTER COLUMN rec_number VARCHAR(36)
GO

ALTER TABLE Production.TransactionHistoryArchive
DROP CONSTRAINT PK_TransactionHistoryArchive_TransactionID

ALTER TABLE Production.TransactionHistoryArchive
DROP CONSTRAINT IF EXISTS PK_TransactionHistoryArchive_TransactionID

ALTER TABLE Production.Transactionhistoryarchive
DROP Pk_transactionhistoryarchive_transactionid

ALTER TABLE [Production].[ProductCostHistory]
WITH CHECK ADD CONSTRAINT [FK_ProductCostHistory_Product_ProductID] FOREIGN KEY([ProductID])
REFERENCES [Production].[Product] ([ProductID])
GO

ALTER TABLE [Production].[ProductCostHistory]
CHECK CONSTRAINT [FK_ProductCostHistory_Product_ProductID]
GO

ALTER TABLE [Production].[ProductCostHistory]
CHECK CONSTRAINT [FK_ProductCostHistory_Product_ProductID]

ALTER TABLE Purchasing.PurchaseOrderHeader
NOCHECK CONSTRAINT FK_PurchaseOrderHeader_Employee_EmployeeID;

ALTER TABLE [dbo].[Attachment]
WITH CHECK
CHECK CONSTRAINT [FK_Attachment_EmailMessage];

ALTER TABLE [dbo].[Attachment]
WITH CHECK
NOCHECK CONSTRAINT [FK_Attachment_EmailMessage];

ALTER TABLE [dbo].[Attachment]
WITH NOCHECK
NOCHECK CONSTRAINT [FK_Attachment_EmailMessage];

ALTER TABLE [dbo].[Attachment]
WITH NOCHECK
CHECK CONSTRAINT [FK_Attachment_EmailMessage];

ALTER TABLE my_table
ADD my_col_1 INT
  , my_col_2 INT
GO

ALTER TABLE TestTable SET (SYSTEM_VERSIONING = ON); GO
ALTER TABLE TestTable SET (SYSTEM_VERSIONING = OFF); GO

ALTER TABLE TestTable SET
  (SYSTEM_VERSIONING = OFF (
    HISTORY_TABLE = TestTableHistory
  ));
GO

ALTER TABLE TestTable SET
  (SYSTEM_VERSIONING = OFF (
    HISTORY_TABLE = TestTableHistory,
    DATA_CONSISTENCY_CHECK = ON
  ));
GO

ALTER TABLE TestTable SET
  (SYSTEM_VERSIONING = OFF (
    HISTORY_TABLE = TestTableHistory,
    DATA_CONSISTENCY_CHECK = ON,
    HISTORY_RETENTION_PERIOD = INFINITE
  ));
GO

ALTER TABLE TestTable SET
  (SYSTEM_VERSIONING = OFF (
    HISTORY_TABLE = TestTableHistory,
    DATA_CONSISTENCY_CHECK = ON,
    HISTORY_RETENTION_PERIOD = 1 YEAR
  ));
GO

ALTER TABLE TestTable SET
  (SYSTEM_VERSIONING = OFF (
    HISTORY_TABLE = TestTableHistory,
    DATA_CONSISTENCY_CHECK = ON,
    HISTORY_RETENTION_PERIOD = 7 MONTHS
  ));
GO

ALTER TABLE TestTable SET (FILESTREAM_ON = "NULL"); GO
ALTER TABLE TestTable SET (FILESTREAM_ON = "default"); GO
ALTER TABLE TestTable SET (FILESTREAM_ON = PartitionSchemeName); GO
ALTER TABLE TestTable SET (DATA_DELETION = ON); GO
ALTER TABLE TestTable SET (DATA_DELETION = OFF(FILTER_COLUMN = ColumnName)); GO
ALTER TABLE TestTable SET (DATA_DELETION = OFF(FILTER_COLUMN = ColumnName, RETENTION_PERIOD = 1 YEAR)); GO
ALTER TABLE TestTable SET (DATA_DELETION = OFF(FILTER_COLUMN = ColumnName, RETENTION_PERIOD = INFINITE)); GO
ALTER TABLE TestTable SET (DATA_DELETION = OFF(FILTER_COLUMN = ColumnName, RETENTION_PERIOD = 7 YEARS)); GO
ALTER TABLE TestTable SET (DATA_DELETION = OFF(FILTER_COLUMN = ColumnName, RETENTION_PERIOD = 7 DAYS)); GO

-- computed columm
-- https://learn.microsoft.com/en-us/sql/relational-databases/tables/specify-computed-columns-in-a-table?view=sql-server-ver16
ALTER TABLE dbo.Products ADD RetailValue AS [QtyAvailable] * UnitPrice * 1.5 PERSISTED; GO
ALTER TABLE dbo.Products ADD RetailValue AS (QtyAvailable * [UnitPrice] * 1.5) PERSISTED NOT NULL; GO
ALTER TABLE dbo.Products ADD InventoyDate AS CAST([InventoryTs] AS date); GO

ALTER TABLE [HangFire].[JobParameter]
ADD CONSTRAINT [FK_HangFire_JobParameter_Job]
FOREIGN KEY ([JobId])
REFERENCES [HangFire].[Job] ([Id])
ON UPDATE CASCADE
ON DELETE CASCADE; GO

-- Drop multiple columns in one statement
ALTER TABLE UserData DROP COLUMN [StrSkill], [StrItem], [StrSerial];
ALTER TABLE UserData DROP COLUMN IF EXISTS StrSkill, StrItem, StrSerial;

-- Check hexadecimal defaults in constraints
CREATE TABLE [dbo].[UserData] (
    [strUserId] [char](21) NOT NULL,
    [strItem] [binary](400) NULL,
    [strSkill] [binary](400) NULL,
    CONSTRAINT PK_UserData PRIMARY KEY CLUSTERED ([strUserId] ASC)
);

ALTER TABLE [dbo].[UserData]
ADD CONSTRAINT [DF_UserData_strSkill] DEFAULT (0x00) FOR [strSkill];
GO

ALTER TABLE [TestTable] DROP PERIOD FOR SYSTEM_TIME;
ALTER TABLE [TestTable] ADD PERIOD FOR SYSTEM_TIME (StartDate, EndDate);

ALTER TABLE [TestTable] REBUILD;
ALTER TABLE [TestTable] REBUILD PARTITION=ALL;
ALTER TABLE [TestTable] REBUILD PARTITION=1;
ALTER TABLE [TestTable] REBUILD WITH (DATA_COMPRESSION=PAGE);
ALTER TABLE [TestTable] REBUILD PARTITION=1 WITH (DATA_COMPRESSION=ROW);
ALTER TABLE [TestTable] REBUILD PARTITION=ALL WITH (DATA_COMPRESSION=COLUMNSTORE ON PARTITIONS (1, 3, 5 TO 6));
