-- https://github.com/sqlfluff/sqlfluff/issues/4218
SET c_date = CURRENT_DATE();

SET ansi_mode = true;

-- Opaque config payloads should parse without SQL expression semantics
SET path = s3a://bucket/path/to/data;

SET key = a-b;

SET warehouse = 's3a://bucket/warehouse';
