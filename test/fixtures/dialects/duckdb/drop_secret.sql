-- https://duckdb.org/docs/stable/sql/statements/create_secret
DROP SECRET s3_chain;

DROP SECRET IF EXISTS "example secret";

DROP TEMPORARY SECRET temporary_secret;

DROP PERSISTENT SECRET persistent_secret FROM local_file;

DROP SECRET IF EXISTS connection_secret FROM connection;

drop secret "quoted name" from memory;
