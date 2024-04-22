-- https://learn.microsoft.com/en-us/sql/t-sql/statements/create-master-key-transact-sql
-- https://learn.microsoft.com/en-us/sql/t-sql/statements/alter-master-key-transact-sql
-- https://learn.microsoft.com/en-us/sql/t-sql/statements/drop-master-key-transact-sql

--CREATE ROLE testuser AUTHORIZATION dbo;



CREATE MASTER KEY ENCRYPTION BY PASSWORD = '<strong password>';

CREATE MASTER KEY;

ALTER MASTER KEY REGENERATE WITH ENCRYPTION BY PASSWORD = '<even stronger password>';

ALTER MASTER KEY FORCE REGENERATE WITH ENCRYPTION BY PASSWORD = '<even stronger password>';

ALTER MASTER KEY ADD ENCRYPTION BY PASSWORD = '<even stronger password>';

ALTER MASTER KEY ADD ENCRYPTION BY SERVICE MASTER KEY;

ALTER MASTER KEY DROP ENCRYPTION BY PASSWORD = '<even stronger password>';

DROP MASTER KEY;
