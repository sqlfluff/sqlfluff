-- https://learn.microsoft.com/en-us/sql/t-sql/statements/alter-table-transact-sql
-- https://learn.microsoft.com/en-us/sql/relational-databases/security/dynamic-data-masking
ALTER TABLE dbo.Membership ALTER COLUMN Email ADD MASKED WITH (FUNCTION = 'email()');

ALTER TABLE dbo.Membership ALTER COLUMN Phone ADD MASKED WITH (FUNCTION = 'partial(1,"xxxxxxx",0)');

ALTER TABLE dbo.Membership ALTER COLUMN Discount ADD MASKED WITH (FUNCTION = 'random(1, 100)');

ALTER TABLE dbo.Membership ALTER COLUMN FirstName ADD MASKED WITH (FUNCTION = N'default()');

ALTER TABLE dbo.Membership ALTER COLUMN LastName ADD MASKED;

ALTER TABLE dbo.Membership ALTER COLUMN Email DROP MASKED;

ALTER TABLE dbo.T1 ALTER COLUMN Id ADD ROWGUIDCOL;

ALTER TABLE dbo.T1 ALTER COLUMN Id DROP ROWGUIDCOL;

ALTER TABLE dbo.T1 ALTER COLUMN Total ADD PERSISTED;

ALTER TABLE dbo.T1 ALTER COLUMN Id DROP NOT FOR REPLICATION;

ALTER TABLE dbo.T1 ALTER COLUMN Notes ADD SPARSE;

ALTER TABLE dbo.T1 ALTER COLUMN ValidFrom ADD HIDDEN;

ALTER TABLE dbo.T1 ALTER COLUMN [ValidTo] DROP HIDDEN;
