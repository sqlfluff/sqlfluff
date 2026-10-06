ATTACH 'file.db';

ATTACH 'file.db' AS file_db;

ATTACH DATABASE 'file.db' AS file_db;

ATTACH 'file.db' (READ_ONLY);

ATTACH 'file.db' AS file_db (READ_ONLY true);

ATTACH 'file.db' (BLOCK_SIZE 16384);

ATTACH 'file.db' (RECOVERY_MODE no_wal_writes);

ATTACH 'sqlite_file.db' AS sqlite_db (TYPE sqlite);

ATTACH 'dbname=postgres' AS pg_db (TYPE postgres, READ_ONLY);

ATTACH 'encrypted.db' AS enc_db (ENCRYPTION_KEY 'quack_quack');

ATTACH 'ducklake:metadata.ducklake' AS my_lake (DATA_PATH 'data_files/');

ATTACH 'file.db' AS "My DB";

ATTACH IF NOT EXISTS 'file.db';

ATTACH IF NOT EXISTS DATABASE 'file.db' AS file_db;

ATTACH OR REPLACE 'file2.db' AS file_db;

ATTACH OR REPLACE DATABASE 'file2.db' AS file_db (READ_ONLY);
