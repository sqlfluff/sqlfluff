-- List all views in default database
SHOW VIEWS;

-- List all views from userdb database
SHOW VIEWS FROM userdb;

-- List all views in global temp view database
SHOW VIEWS IN global_temp;

-- List all views from default database matching the pattern `sam*`
SHOW VIEWS FROM default LIKE 'sam*';

-- List all views from the current database
-- matching the pattern `sam|suj｜temp*`
SHOW VIEWS LIKE 'sam|suj|temp*';

-- List all views from default database matching the pattern `sam*`
-- without LIKE keyword
SHOW VIEWS FROM default 'sam*';

-- List all views from the current database
-- matching the pattern `sam|suj｜temp*` without LIKE keyword
SHOW VIEWS 'sam|suj|temp*';
