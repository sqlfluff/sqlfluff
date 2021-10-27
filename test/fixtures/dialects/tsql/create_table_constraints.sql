CREATE TABLE [dbo].[example](
    [Column A] [int] IDENTITY,
    [Column B] [int] IDENTITY(1, 1) NOT NULL,
    [ColumnC] varchar(100) DEFAULT 'mydefault',
    [ColumnDecimal] DATE DEFAULT GETDATE()
)
