LOCKING DATABASE database_name FOR ACCESS
SELECT a FROM database.mytable;

LOCKING TABLE table_name FOR READ
SELECT a FROM table_name;

LOCK ROW FOR WRITE
SELECT a FROM table_name;
