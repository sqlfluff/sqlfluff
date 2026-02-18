-- Basic model from another model
CREATE MODEL my_model
  FROM MODEL source_model;

-- With version
CREATE OR REPLACE MODEL my_model
  WITH VERSION v1
  FROM MODEL source_model VERSION v2;

-- From stage
CREATE MODEL IF NOT EXISTS my_model
  FROM @my_stage/models/my_model;
