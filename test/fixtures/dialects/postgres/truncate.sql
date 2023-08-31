TRUNCATE bigtable;
TRUNCATE some_schema.bigtable;
TRUNCATE TABLE bigtable;
TRUNCATE ONLY bigtable;
TRUNCATE TABLE ONLY bigtable;
TRUNCATE bigtable *;
TRUNCATE TABLE bigtable *;
TRUNCATE bigtable, fattable;
TRUNCATE TABLE bigtable, fattable;
TRUNCATE ONLY bigtable, fattable *;
TRUNCATE bigtable RESTART IDENTITY;
TRUNCATE bigtable CONTINUE IDENTITY;
TRUNCATE bigtable CASCADE;
TRUNCATE bigtable RESTRICT;
TRUNCATE TABLE
    ONLY bigtable,
    fattable *,
    ONLY slimtable
CONTINUE IDENTITY CASCADE;
