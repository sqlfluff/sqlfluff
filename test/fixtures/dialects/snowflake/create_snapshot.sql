-- Basic snapshot
CREATE SNAPSHOT my_snapshot
  FROM SERVICE my_service
  VOLUME 'data_vol'
  INSTANCE 0;

-- OR REPLACE with comment
CREATE OR REPLACE SNAPSHOT my_snapshot
  FROM SERVICE my_service
  VOLUME 'block_vol'
  INSTANCE 1
  COMMENT = 'daily backup'
  TAG (env = 'prod');

-- IF NOT EXISTS
CREATE SNAPSHOT IF NOT EXISTS my_snapshot
  FROM SERVICE my_db.my_schema.my_service
  VOLUME 'logs'
  INSTANCE 0;
