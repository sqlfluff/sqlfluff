ALTER STREAMLIT my_streamlit SET
ROOT_LOCATION = '@stage_name/folder'
MAIN_FILE = 'main.py';

ALTER STREAMLIT my_streamlit SET
ROOT_LOCATION = '@stage_name/folder'
MAIN_FILE = 'main.py'
QUERY_WAREHOUSE = my_wh;

ALTER STREAMLIT my_streamlit SET
ROOT_LOCATION = '@stage_name/folder'
MAIN_FILE = 'main.py'
QUERY_WAREHOUSE = my_wh
comment = 'New comment for stream';

ALTER STREAMLIT my_streamlit RENAME TO new_my_streamlit;
