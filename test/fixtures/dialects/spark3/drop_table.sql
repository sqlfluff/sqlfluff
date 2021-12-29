-- Drop TABLE with all optional syntax
DROP TABLE IF EXISTS table_identifier;

-- Assumes a table named `employeetable` exists.
DROP TABLE employeetable;

-- Assumes a table named `employeetable` exists in the `userdb` database
DROP TABLE userdb.employeetable;

-- Assumes a table named `employeetable` does not exist,Try with IF EXISTS
-- will not throw exception
DROP TABLE IF EXISTS employeetable;
