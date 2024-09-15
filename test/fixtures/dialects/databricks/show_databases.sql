-- Lists all databases
SHOW DATABASES;

-- List all databases from userdb catalog
SHOW DATABASES FROM userdb;

-- List all databases in userdb catalog
SHOW DATABASES IN userdb;

-- List all databases from default catalog matching the pattern `sam*`
SHOW DATABASES FROM default LIKE 'sam*';

-- List all databases from default catalog matching the pattern `sam*`
-- without LIKE keyword
SHOW DATABASES FROM default 'sam*';

-- List all databases matching the pattern `sam*|suj` without LIKE keyword
SHOW DATABASES 'sam*|suj';

-- Lists all databases. Keywords SCHEMAS and DATABASES are interchangeable.
SHOW SCHEMAS;
