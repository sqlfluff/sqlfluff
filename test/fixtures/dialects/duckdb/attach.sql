ATTACH 'file.db';

ATTACH 'file.db' AS mydb;

ATTACH 'file.db' AS mydb (READ_ONLY);

ATTACH IF NOT EXISTS 'file.db' AS mydb;

ATTACH DATABASE 'file.db' AS file_db;

ATTACH OR REPLACE 'file2.db' AS file_db;

ATTACH 'file.db' AS mydb (TYPE sqlite);

ATTACH 'file.db' AS mydb (READ_ONLY, TYPE sqlite);

DETACH mydb;

DETACH DATABASE IF EXISTS mydb;
