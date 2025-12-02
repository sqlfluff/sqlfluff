-- Create a synonym
CREATE SYNONYM my_synonym FOR mytable;

-- Create a synonym for a multi-part schema
CREATE SYNONYM my_synonym FOR otherdb.dbo.mytable;

-- Drop a synonym
DROP SYNONYM my_synonym;

-- Conditionally drop synonym
DROP SYNONYM IF EXISTS my_synonym;

-- Conditionally drop synonym with schema
DROP SYNONYM IF EXISTS dbo.my_synonym;
