create or replace procedure sp_pi()
    returns float not null
    language javascript
    as
    $$
    return 3.1415926;
    $$
    ;

create or replace procedure stproc1(FLOAT_PARAM1 FLOAT)
    returns string
    language javascript
    strict
    execute as owner
    as
    $$
    var sql_command =
     "INSERT INTO stproc_test_table1 (num_col1) VALUES (" + FLOAT_PARAM1 + ")";
    try {
        snowflake.execute (
            {sqlText: sql_command}
            );
        return "Succeeded.";   // Return a success/error indicator.
        }
    catch (err)  {
        return "Failed: " + err;   // Return a success/error indicator.
        }
    $$
    ;

CREATE OR REPLACE PROCEDURE public.test_procedure (test_table VARCHAR(), test_col VARCHAR())
RETURNS VARCHAR()
LANGUAGE JAVASCRIPT
AS
$$
try {
    var sql_command = "ALTER TABLE " + test_table + " DROP " + tet_col;
    snowflake.execute ({sqlText: sql_command});
    return "Succeeded.";
}
catch (err) {
   return "Failed: execute "+ sql_command +". Error : "+ err;   // Return a success/error indicator.
}
$$
;

CREATE OR REPLACE PROCEDURE UTIL_DB.PUBLIC.PROCEDURE_WITHOUT_EXPLICIT_LANGUAGE()
RETURNS INT
AS
$$
BEGIN
    RETURN 1;
END
$$;

CREATE OR REPLACE PROCEDURE UTIL_DB.PUBLIC.PROCEDURE_LANGUAGE_SQL()
RETURNS INT
LANGUAGE SQL
AS
$$
BEGIN
    RETURN 1;
END
$$;


create or replace procedure UTIL_DB.PUBLIC.PROCEDURE_LANGUAGE_PYTHON()
  returns variant
  language python
  runtime_version = '3.8'
  packages = ('numpy','pandas','xgboost==1.5.0')
  handler = 'udf'
  comment = 'hello_world'
as $$
import numpy as np
import pandas as pd
import xgboost as xgb
def udf():
    return [np.__version__, pd.__version__, xgb.__version__]
$$;


create or replace procedure UTIL_DB.PUBLIC.PROCEDURE_LANGUAGE_JAVA(x varchar)
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


CREATE OR REPLACE PROCEDURE filter_by_role(table_name VARCHAR, role VARCHAR)
RETURNS INT --TABLE()
LANGUAGE SCALA
RUNTIME_VERSION = '2.12'
PACKAGES = ('com.snowflake:snowpark:latest')
HANDLER = 'Filter.filterByRole'
AS
$$
import com.snowflake.snowpark.functions._
import com.snowflake.snowpark._

object Filter {
    def filterByRole(session: Session, tableName: String, role: String): DataFrame = {
        val table = session.table(tableName)
        val filteredRows = table.filter(col("role") === role)
        return filteredRows
    }
}
$$;

CREATE OR REPLACE PROCEDURE myprocedure(
"Id" NUMBER(38,0)
)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
-- Snowflake Scripting code
DECLARE
radius_of_circle FLOAT;
area_of_circle FLOAT;
BEGIN
radius_of_circle := 3;
area_of_circle := pi() * radius_of_circle * radius_of_circle;
RETURN area_of_circle;
END;
$$
;

CREATE OR REPLACE PROCEDURE MY_PROCEDURE(
"Id" NUMBER(38,0)
)
RETURNS VARCHAR
LANGUAGE SQL
AS
BEGIN
select 1;
select 2;
select 3;
select 4;
return 5;
END;
