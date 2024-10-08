-- Minimal stored procedure
CREATE PROC [PROCEDURE_NAME]
AS
BEGIN
	SELECT 1;
END;
GO

CREATE PROCEDURE [dbo].[TEST]
AS
BEGIN
	SELECT 1;
END;
GO

ALTER PROC [PROCEDURE_NAME]
AS
BEGIN
	SELECT 1;
END;
GO

ALTER PROCEDURE [PROCEDURE_NAME]
AS
BEGIN
	SELECT 1;
END;
GO

CREATE OR ALTER PROC [PROCEDURE_NAME]
AS
BEGIN
	SELECT 1;
END;
GO

CREATE OR ALTER PROCEDURE [PROCEDURE_NAME]
AS
BEGIN
	SELECT 1;
END;
GO

-- Stored procedure with parameters
CREATE PROCEDURE [dbo].[TEST] (@id UNIQUEIDENTIFIER)
AS
	SELECT 1;
GO

CREATE PROCEDURE [dbo].[TEST] (
	@id UNIQUEIDENTIFIER NULL = NULL,
	@fooReadonly NVARCHAR(42) = N'foo' READONLY,
	@bar BIT VARYING NULL = NULL OUTPUT,
	@output TINYINT OUT
)
AS
BEGIN
	SET @output = (
		SELECT tinyint_value
		FROM dbo.TEST
	);

	IF @id IS NULL
	BEGIN
		SELECT @bar, @fooReadonly;
	END;
END;
GO

CREATE PROCEDURE [dbo].[TEST] (
	@id UNIQUEIDENTIFIER NULL = NULL,
	@bar NVARCHAR(32) NULL = NULL
)
WITH ENCRYPTION, RECOMPILE, EXECUTE AS 'sa'
AS
BEGIN
	SELECT 1;
END;
GO

CREATE PROCEDURE [dbo].[TEST] (
	@id UNIQUEIDENTIFIER NULL = NULL,
	@bar NVARCHAR(32) NULL = NULL
)
WITH ENCRYPTION, RECOMPILE, EXECUTE AS 'sa'
FOR REPLICATION
AS
BEGIN
	SELECT @id, @bar;
END;
GO

-- Natively compiled stored procedure
CREATE OR ALTER PROCEDURE [dbo].[TEST] (@id INT NOT NULL)
WITH NATIVE_COMPILATION, SCHEMABINDING, EXECUTE AS OWNER
AS
BEGIN ATOMIC WITH (
	LANGUAGE = N'us_english',
	TRANSACTION ISOLATION LEVEL = SERIALIZABLE,
	DATEFIRST = 10,
	DATEFORMAT = dym,
	DELAYED_DURABILITY = ON
)
	SELECT 1;
END;
GO

CREATE OR ALTER PROCEDURE [dbo].[TEST] (@id INT NOT NULL)
WITH NATIVE_COMPILATION, SCHEMABINDING, EXECUTE AS OWNER
AS
BEGIN ATOMIC WITH (
	TRANSACTION ISOLATION LEVEL = SNAPSHOT,
	LANGUAGE = 'us_english'
)
	SELECT 1;
END;
GO

CREATE OR ALTER PROCEDURE [dbo].[TEST] (@id INT NOT NULL)
WITH NATIVE_COMPILATION, SCHEMABINDING, EXECUTE AS OWNER
AS
BEGIN ATOMIC WITH (
	TRANSACTION ISOLATION LEVEL = REPEATABLE READ,
	LANGUAGE = N'us_english',
	DELAYED_DURABILITY = OFF,
	DATEFORMAT = myd
)
	SELECT 1;
END;
GO

-- CLR stored procedure
CREATE PROCEDURE [dbo].[TEST]
AS
EXTERNAL NAME [dbo].[class_name].[static_method];
GO

CREATE PROCEDURE [dbo].[TEST]; 1064
AS
EXTERNAL NAME [dbo].[class_name].[static_method];
GO

CREATE OR ALTER PROCEDURE [dbo].[TEST] (
    @id UNIQUEIDENTIFIER = NEWID(),
    @output NVARCHAR(32) OUTPUT,
    @activated BIT OUT READONLY
)
WITH EXECUTE AS 'sa'
AS EXTERNAL NAME [dbo].[class_name].[static_method];
GO

CREATE OR ALTER PROCEDURE dbo.DoSomething
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
END
GO

CREATE OR ALTER PROCEDURE dbo.DoSomething
AS
BEGIN
    SET NOCOUNT, XACT_ABORT ON;
END
GO
