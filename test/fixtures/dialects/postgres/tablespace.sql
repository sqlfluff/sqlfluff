CREATE TABLESPACE dbspace LOCATION '/data/dbs';

CREATE TABLESPACE indexspace OWNER genevieve LOCATION '/data/indexes';

CREATE TABLESPACE fastspace OWNER CURRENT_USER LOCATION '/ssd1/postgresql/data'
WITH (random_page_cost = 1.1, effective_io_concurrency = 200);

ALTER TABLESPACE index_space RENAME TO fast_raid;

ALTER TABLESPACE index_space OWNER TO mary;

ALTER TABLESPACE index_space OWNER TO SESSION_USER;

ALTER TABLESPACE index_space SET (seq_page_cost = 1.0, random_page_cost = 1.5);

ALTER TABLESPACE index_space RESET (random_page_cost);

DROP TABLESPACE mystuff;

DROP TABLESPACE IF EXISTS mystuff;
