-- Drop FUNCTION with all optional syntax
DROP VIEW IF EXISTS view_identifier;

-- Assumes a view named `employeeView` exists.
DROP VIEW employeeview;

-- Assumes a view named `employeeView` exists in the `userdb` database
DROP VIEW userdb.employeeview;

-- Assumes a view named `employeeView` does not exist,Try with IF EXISTS
-- will not throw exception
DROP VIEW IF EXISTS employeeview;
