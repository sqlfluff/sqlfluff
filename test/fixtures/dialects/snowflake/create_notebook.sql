-- Basic notebook
CREATE NOTEBOOK my_notebook;

-- OR REPLACE with options
CREATE OR REPLACE NOTEBOOK my_notebook
  FROM '@my_stage/notebooks/analysis.ipynb'
  MAIN_FILE = 'analysis.ipynb'
  QUERY_WAREHOUSE = my_wh
  COMMENT = 'data analysis notebook';

-- With compute options
CREATE NOTEBOOK IF NOT EXISTS my_notebook
  IDLE_AUTO_SHUTDOWN_TIME_SECONDS = 7200
  RUNTIME_NAME = 'SYSTEM$GPU_RUNTIME'
  COMPUTE_POOL = 'my_pool'
  WAREHOUSE = my_wh;
