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

ATTACH OR REPLACE IF NOT EXISTS 'file.db' AS mydb;

ATTACH 'file.db' (BLOCK_SIZE 16384);

ATTACH 'file.db' (RECOVERY_MODE no_wal_writes, READ_ONLY true);

ATTACH 'encrypted.db' AS enc_db (ENCRYPTION_KEY 'quack_quack', ENCRYPTION_CIPHER 'CBC');

ATTACH getenv('DATABASE_PATH') AS env_db;
