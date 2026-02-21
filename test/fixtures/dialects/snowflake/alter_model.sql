-- Set comment
ALTER MODEL my_model SET
  COMMENT = 'production model'
  DEFAULT_VERSION = 'v2';

-- Unset comment
ALTER MODEL my_model UNSET COMMENT;

-- Set version alias
ALTER MODEL my_model VERSION v1 SET ALIAS = 'production';

-- Unset version alias
ALTER MODEL my_model VERSION v1 UNSET ALIAS;

-- Rename
ALTER MODEL IF EXISTS my_model RENAME TO new_model;

-- Set tag
ALTER MODEL my_model SET
  TAG my_tag = 'ml_model';

-- Unset tag
ALTER MODEL my_model UNSET TAG my_tag;
