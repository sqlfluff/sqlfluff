CREATE JAVA ADAPTER SCRIPT my_script AS
%jar hive_jdbc_adapter.jar;
/

CREATE OR REPLACE PYTHON ADAPTER SCRIPT test.adapter_dummy AS
def adapter_call(in_json):
 return "BLABLA"
/

CREATE OR REPLACE LUA ADAPTER SCRIPT test.adapter_dummy AS
function adapter_call(in_json):
 return 'BLABLA'
/
