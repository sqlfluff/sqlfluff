CREATE OR REPLACE IMAGE REPOSITORY tutorial_repository;

CREATE OR REPLACE IMAGE REPOSITORY tutorial_repository
ENCRYPTION = (type = 'SNOWFLAKE_SSE');

CREATE IMAGE REPOSITORY tutorial_repository
  COMMENT = 'Repository for tutorial images'
  WITH TAG (cost_center = 'engineering');

CREATE IMAGE REPOSITORY IF NOT EXISTS my_db.my_schema.my_repository
  ENCRYPTION = (TYPE = 'SNOWFLAKE_FULL')
  TAG (cost_center = 'engineering', env = 'dev');

ALTER IMAGE REPOSITORY tutorial_repository SET COMMENT = 'Images for the tutorial services';

ALTER IMAGE REPOSITORY tutorial_repository UNSET COMMENT;

ALTER IMAGE REPOSITORY IF EXISTS tutorial_repository SET TAG cost_center = 'finance', env = 'dev';

ALTER IMAGE REPOSITORY tutorial_repository UNSET TAG cost_center, env;

DROP IMAGE REPOSITORY tutorial_repository;

DROP IMAGE REPOSITORY IF EXISTS tutorial_repository;

SHOW IMAGE REPOSITORIES;

SHOW IMAGE REPOSITORIES IN SCHEMA;

SHOW IMAGE REPOSITORIES IN SCHEMA sc1;

SHOW IMAGE REPOSITORIES IN DATABASE db1;

SHOW IMAGE REPOSITORIES IN ACCOUNT;

SHOW IMAGE REPOSITORIES LIKE 'tutorial%' IN DATABASE db1 STARTS WITH 'tu' LIMIT 10 FROM 'tutorial_a';

SHOW IMAGES IN IMAGE REPOSITORY tutorial_db.data_schema.tutorial_repository;

GRANT READ ON IMAGE REPOSITORY tutorial_repository TO ROLE my_role;

GRANT READ, WRITE ON IMAGE REPOSITORY tutorial_repository TO ROLE my_role;

GRANT CREATE IMAGE REPOSITORY ON SCHEMA my_schema TO ROLE my_role;

-- The new keywords are not reserved.
SELECT image, images FROM my_table;
