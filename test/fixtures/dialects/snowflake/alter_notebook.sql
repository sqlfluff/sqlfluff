-- Rename
ALTER NOTEBOOK my_notebook RENAME TO new_notebook;

-- Set properties
ALTER NOTEBOOK IF EXISTS my_notebook SET
  COMMENT = 'updated notebook'
  QUERY_WAREHOUSE = new_wh
  IDLE_AUTO_SHUTDOWN_TIME_SECONDS = 3600;

-- Unset properties
ALTER NOTEBOOK my_notebook UNSET QUERY_WAREHOUSE, COMMENT;
