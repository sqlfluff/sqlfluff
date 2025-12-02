UPDATE HumanResources.Employee
SET JobTitle = N'Executive'
WHERE NationalIDNumber = 123456789
IF @@ROWCOUNT = 0
PRINT 'Warning: No rows were updated';
IF @@ERROR = 547
    BEGIN
    PRINT N'A check constraint violation occurred.';
    END
GO

SELECT @@IDENTITY AS 'Identity';
GO

PRINT @@TRANCOUNT
GO

SELECT @@PACK_RECEIVED AS 'Packets Received';
GO
