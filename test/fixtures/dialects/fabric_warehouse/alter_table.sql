ALTER TABLE dbo.customer ADD region_name VARCHAR(100) NULL;
ALTER TABLE dbo.customer DROP COLUMN region_name;
ALTER TABLE dbo.customer ADD CONSTRAINT UQ_customer UNIQUE NONCLUSTERED (customer_name) NOT ENFORCED;
ALTER TABLE dbo.customer DROP CONSTRAINT UQ_customer;
ALTER TABLE dbo.customer ALTER COLUMN customer_name VARCHAR(300) NOT NULL;
