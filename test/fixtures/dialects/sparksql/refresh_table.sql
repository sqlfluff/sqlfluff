-- The cached entries of the table will be refreshed
-- The table is resolved from the current database as
--   the table name is unqualified.
REFRESH TABLE tbl1;
REFRESH tbl1;

-- The cached entries of the view will be refreshed or invalidated
-- The view is resolved from tempDB database, as the view
--   name is qualified.
REFRESH TABLE tempdb.view1;
REFRESH tempdb.view1;
