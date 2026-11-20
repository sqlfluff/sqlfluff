CREATE NOTEBOOK my_notebook;

CREATE OR REPLACE NOTEBOOK my_notebook
QUERY_WAREHOUSE = my_wh;

CREATE NOTEBOOK IF NOT EXISTS my_notebook
FROM '@my_db.my_schema.my_stage'
MAIN_FILE = 'my_notebook.ipynb'
QUERY_WAREHOUSE = my_wh;

CREATE NOTEBOOK my_notebook
FROM '@my_db.my_schema.my_stage'
MAIN_FILE = 'my_notebook.ipynb'
QUERY_WAREHOUSE = my_wh
COMMENT = 'amazing comment';

CREATE NOTEBOOK my_notebook
RUNTIME_NAME = 'SYSTEM$BASIC_RUNTIME'
COMPUTE_POOL = 'my_compute_pool'
IDLE_AUTO_SHUTDOWN_TIME_SECONDS = 3600;

CREATE NOTEBOOK my_notebook
RUNTIME_NAME = 'SYSTEM$GPU_RUNTIME'
COMPUTE_POOL = 'gpu_pool_1';

CREATE NOTEBOOK my_notebook
QUERY_WAREHOUSE = my_wh
WAREHOUSE = my_runtime_wh;

CREATE NOTEBOOK my_db.my_schema.my_notebook
MAIN_FILE = 'my_notebook.ipynb'
FROM '@my_db.my_schema.my_stage';
