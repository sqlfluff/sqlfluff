-- List all tables in default database
SHOW TABLES;

-- List all tables from userdb database
SHOW TABLES FROM userdb;

-- List all tables in userdb database
SHOW TABLES IN userdb;

-- List all tables from default database matching the pattern `sam*`
SHOW TABLES FROM default LIKE 'sam*';

-- List all tables from default database matching the pattern `sam*`
-- without LIKE keyword
SHOW TABLES FROM default 'sam*';

-- List all tables matching the pattern `sam*|suj` without LIKE keyword
SHOW TABLES 'sam*|suj';
