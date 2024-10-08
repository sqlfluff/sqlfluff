CREATE FUNCTION pi_udf()
  RETURNS FLOAT
  AS '3.141592654::FLOAT';
CREATE FUNCTION simple_table_function ()
  RETURNS TABLE (x INTEGER, y INTEGER)
  AS
  $$
    SELECT 1, 2
    UNION ALL
    SELECT 3, 4
  $$;
CREATE OR REPLACE FUNCTION get_countries_for_user ( id number )
  RETURNS TABLE (country_code char, country_name varchar)
  RETURNS NULL ON NULL INPUT
  AS 'select distinct c.country_code, c.country_name
      from user_addresses a, countries c
      where a.user_id = id
      and c.country_code = a.country_code';
CREATE SECURE FUNCTION js_factorial(d double)
  RETURNS double
  IMMUTABLE
  LANGUAGE JAVASCRIPT
  STRICT
  AS '
  if (D <= 0) {
    return 1;
  } else {
    var result = 1;
    for (var i = 2; i <= D; i++) {
      result = result * i;
    }
    return result;
  }
  ';

CREATE FUNCTION IF NOT EXISTS simple_table_function ()
  RETURNS TABLE (x INTEGER, y INTEGER)
  LANGUAGE SQL
  AS
  $$
    SELECT 1, 2
    UNION ALL
    SELECT 3, 4
  $$;

create function my_decrement_udf(i numeric(9, 0))
    returns numeric
    language java
    imports = ('@~/my_decrement_udf_package_dir/my_decrement_udf_jar.jar')
    handler = 'my_decrement_udf_package.my_decrement_udf_class.my_decrement_udf_method'
    ;

create or replace function echo_varchar(x varchar)
returns varchar
language java
called on null input
handler='TestFunc.echoVarchar'
target_path='@~/testfunc.jar'
as
'class TestFunc {
  public static String echoVarchar(String x) {
    return x;
  }
}';

create or replace function py_udf()
  returns variant
  language python
  runtime_version = '3.8'
  packages = ('numpy','pandas','xgboost==1.5.0')
  handler = 'udf'
as $$
import numpy as np
import pandas as pd
import xgboost as xgb
def udf():
    return [np.__version__, pd.__version__, xgb.__version__]
$$;

create or replace function dream(i int)
  returns variant
  language python
  runtime_version = '3.8'
  handler = 'sleepy.snore'
  imports = ('@my_stage/sleepy.py')
;

create or replace function addone(i int)
returns int
language python
runtime_version = '3.8'
handler = 'addone_py'
as
$$
def addone_py(i):
  return i+1
$$;

CREATE OR REPLACE FUNCTION echo_varchar(x VARCHAR)
RETURNS VARCHAR
LANGUAGE SCALA
RUNTIME_VERSION = '2.12'
HANDLER='Echo.echoVarchar'
AS
$$
class Echo {
  def echoVarchar(x : String): String = {
    return x
  }
}
$$;

CREATE OR REPLACE FUNCTION google_translate_python(sentence STRING, language STRING)
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = '3.8'
HANDLER = 'get_translation'
EXTERNAL_ACCESS_INTEGRATIONS = (google_apis_access_integration, my_integration )
PACKAGES = ('snowflake-snowpark-python','requests')
SECRETS = ('cred' = oauth_token, 'cred2' = DATA_STAGE.AWS_SECRET_KEY )
AS
$$
import _snowflake
import requests
import json
session = requests.Session()
def get_translation(sentence, language):
  token = _snowflake.get_oauth_access_token('cred')
  url = "https://translation.googleapis.com/language/translate/v2"
  data = {'q': sentence,'target': language}
  response = session.post(url, json = data, headers = {"Authorization": "Bearer " + token})
  return response.json()['data']['translations'][0]['translatedText']
$$;


create or replace aggregate function addone(i int)
returns int
language python
runtime_version = '3.8'
handler = 'addone_py'
as
$$
def addone_py(i):
  return i+1
$$;


CREATE OR REPLACE FUNCTION TEST_DB.TEST_SCHEMA.TEST_TABLE(
  COL_1 VARCHAR DEFAULT NULL
  , COL_2 VARCHAR DEFAULT NULL
)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
SELECT
        CASE
            WHEN (LOWER(COL_1) IS NOT NULL AND
                        LOWER(COL_2) = 'test_marketing')
                THEN 'marketing_channel'
            ELSE '(Other)'
END
$$;;

CREATE TEMPORARY FUNCTION pi_udf()
  RETURNS FLOAT
  AS '3.141592654::FLOAT';

CREATE TEMP FUNCTION pi_udf()
  RETURNS FLOAT
  AS '3.141592654::FLOAT';
