-- Create FUNCTION with all optional syntax
CREATE OR REPLACE TEMPORARY FUNCTION IF NOT EXISTS
function_name AS "class_name" USING FILE "resource_locations";

-- Create a permanent function called `simple_udf`.
CREATE FUNCTION simple_udf AS 'SimpleUdf'
USING JAR '/tmp/SimpleUdf.jar';

-- Created a temporary function.
CREATE TEMPORARY FUNCTION simple_temp_udf AS 'SimpleUdf'
USING JAR '/tmp/SimpleUdf.jar';

-- Replace the implementation of `simple_udf`
CREATE OR REPLACE FUNCTION simple_udf AS 'SimpleUdfR'
USING JAR '/tmp/SimpleUdfR.jar';

-- Create a permanent function `test_avg`
CREATE FUNCTION test_avg
AS 'org.apache.hadoop.hive.ql.udf.generic.GenericUDAFAverage';

---- Create Temporary function `test_avg`
CREATE TEMPORARY FUNCTION test_avg
AS 'org.apache.hadoop.hive.ql.udf.generic.GenericUDAFAverage';
