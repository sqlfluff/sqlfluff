CREATE TRIGGER reminder1
ON Sales.Customer
AFTER INSERT, UPDATE
AS RAISERROR ('Notify Customer Relations', 16, 10);
GO

CREATE TRIGGER reminder2
ON Sales.Customer
AFTER INSERT, UPDATE, DELETE
AS
   EXEC msdb.dbo.sp_send_dbmail
        @profile_name = 'AdventureWorks2012 Administrator',
        @recipients = 'danw@Adventure-Works.com',
        @body = 'Don''t forget to print a report for the sales force.',
        @subject = 'Reminder';
GO

CREATE TRIGGER Purchasing.LowCredit ON Purchasing.PurchaseOrderHeader
AFTER INSERT
AS
IF (ROWCOUNT_BIG() = 0)
RETURN;
IF EXISTS (SELECT 1
           FROM inserted AS i
           JOIN Purchasing.Vendor AS v
           ON v.BusinessEntityID = i.VendorID
           WHERE v.CreditRating = 5
          )
BEGIN
RAISERROR ('A vendor''s credit rating is too low to accept new
purchase orders.', 16, 1);
ROLLBACK TRANSACTION;
RETURN
END;
GO


CREATE TRIGGER safety
ON DATABASE
FOR DROP_SYNONYM
AS
IF (@@ROWCOUNT = 0)
RETURN;
   RAISERROR ('You must disable Trigger "safety" to remove synonyms!', 10, 1)
   ROLLBACK
GO
DROP TRIGGER safety
ON DATABASE;
GO

CREATE TRIGGER ddl_trig_database
ON ALL SERVER
FOR CREATE_DATABASE
AS
    PRINT 'Database Created.'
    SELECT 1
GO

CREATE TRIGGER ddl_trig_database
ON ALL SERVER
FOR CREATE_DATABASE
AS
    PRINT 'Database Created.';
    SELECT 1
GO

DROP TRIGGER ddl_trig_database
ON ALL SERVER;
GO

CREATE TRIGGER connection_limit_trigger
ON ALL SERVER WITH EXECUTE AS 'login_test'
FOR LOGON
AS
BEGIN
IF ORIGINAL_LOGIN()= 'login_test' AND
    (SELECT COUNT(*) FROM sys.dm_exec_sessions
            WHERE is_user_process = 1 AND
                original_login_name = 'login_test') > 3
    ROLLBACK;
END;
GO

Create TRIGGER dbo.tr_SP_BALS_L2_ATTRIBUTES
ON dbo.SP_BALS_L2_ATTRIBUTES
  AFTER UPDATE
  AS
  UPDATE dbo.SP_BALS_L2_ATTRIBUTES
  SET PDW_LAST_UPDATED = Getdate()
  FROM dbo.SP_BALS_L2_ATTRIBUTES o
  INNER JOIN Inserted i
  ON
     o.PK_L2_BALS = i.PK_L2_BALS
go

disable trigger dbo.tr_SP_BALS_L2_ATTRIBUTES on dbo.SP_BALS_L2_ATTRIBUTES
go


Create TRIGGER dbo.tr_u_SP_BALS_L2_ATTRIBUTES
ON dbo.SP_BALS_L2_ATTRIBUTES
  AFTER UPDATE
  AS
  UPDATE dbo.SP_BALS_L2_ATTRIBUTES
  SET PDW_LAST_UPDATED = sysdatetime()
  FROM dbo.SP_BALS_L2_ATTRIBUTES o
  INNER JOIN Inserted i
  ON
     o.PK_L2_BALS = i.PK_L2_BALS
GO

DROP TRIGGER employee_insupd;
GO

DROP TRIGGER safety
ON DATABASE;
GO

disable trigger dbo.tr_u_SP_BALS_L2_ATTRIBUTES on dbo.SP_BALS_L2_ATTRIBUTES
GO

DISABLE TRIGGER safety ON DATABASE;
GO

CREATE OR ALTER TRIGGER reminder1
ON Sales.Customer
AFTER INSERT, UPDATE
AS RAISERROR ('Notify Customer Relations', 16, 10);
GO

CREATE TRIGGER reminder
ON person.address
AFTER UPDATE
AS
IF (UPDATE(stateprovinceid) OR UPDATE(postalcode))
    BEGIN
        RAISERROR (50009, 16, 10)
    END;
GO
