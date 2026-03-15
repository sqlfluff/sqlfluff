-- ALTER SYSTEM SET with equals sign
ALTER SYSTEM SET max_wal_size = '2GB';

-- ALTER SYSTEM SET with TO
ALTER SYSTEM SET work_mem TO '64MB';

-- ALTER SYSTEM SET to DEFAULT
ALTER SYSTEM SET shared_buffers = DEFAULT;

-- ALTER SYSTEM SET with numeric value
ALTER SYSTEM SET max_connections = 200;

-- ALTER SYSTEM SET with delimited values
ALTER SYSTEM SET search_path = public, pg_catalog;

-- ALTER SYSTEM RESET parameter
ALTER SYSTEM RESET max_wal_size;

-- ALTER SYSTEM RESET ALL
ALTER SYSTEM RESET ALL;
