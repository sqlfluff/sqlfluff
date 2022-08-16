CREATE TABLE [dbo].[example](
    [Column A] [int] IDENTITY,
    [Column B] [int] IDENTITY(1, 1) NOT NULL,
    [ColumnC] varchar(100) DEFAULT 'mydefault',
    [ColumnDecimal] DATE DEFAULT GETDATE(),
    [col1] int default ((-1)) not null,
    [col1] int default (-1) not null,
    [col1] int default -1 not null,
    [col1] INT DEFAULT (NULL) NULL
)
GO

create table [schema1].[table1] (
	[col1] INT
	, PRIMARY KEY CLUSTERED ([col1] ASC)
)
GO

create table [schema1].[table1] (
	[col1] INT
	, CONSTRAINT [Pk_Id] PRIMARY KEY NONCLUSTERED ([col1] DESC)
)
GO

CREATE TABLE [dbo].[table1] (
    [ColumnB] [varchar](100) FILESTREAM MASKED WITH (FUNCTION = 'my_func'),
    [ColumnC] varchar(100) NULL NOT FOR REPLICATION,
    [ColumnDecimal] decimal(10,3) GENERATED ALWAYS AS ROW START HIDDEN,
    [columnE] varchar(100) ENCRYPTED WITH (COLUMN_ENCRYPTION_KEY = key_name,
                                          ENCRYPTION_TYPE = RANDOMIZED,
                                            ALGORITHM = 'AEAD_AES_256_CBC_HMAC_SHA_256'
                                            ),
    [column1] varchar (100) collate Latin1_General_BIN
)
GO
