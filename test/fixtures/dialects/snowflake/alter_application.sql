-- Set properties
ALTER APPLICATION my_app SET
  COMMENT = 'updated app'
  DEBUG_MODE = FALSE;

-- Unset properties
ALTER APPLICATION my_app UNSET COMMENT, DEBUG_MODE;

-- Rename
ALTER APPLICATION IF EXISTS my_app RENAME TO new_app;

-- Upgrade
ALTER APPLICATION my_app UPGRADE;

-- Upgrade with version
ALTER APPLICATION my_app UPGRADE
  USING VERSION v2 PATCH 1;
