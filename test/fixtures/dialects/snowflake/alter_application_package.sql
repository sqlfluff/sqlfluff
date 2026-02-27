-- Set properties
ALTER APPLICATION PACKAGE my_package SET
  DISTRIBUTION = EXTERNAL
  COMMENT = 'public package';

-- Unset properties
ALTER APPLICATION PACKAGE IF EXISTS my_package UNSET
  DATA_RETENTION_TIME_IN_DAYS, COMMENT;

-- Set tag
ALTER APPLICATION PACKAGE my_package SET
  TAG my_tag = 'value';

-- Unset tag
ALTER APPLICATION PACKAGE my_package UNSET
  TAG my_tag;
