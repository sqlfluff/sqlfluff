-- Create FUNCTION with all optional syntax
CREATE OR REPLACE TEMPORARY FUNCTION IF NOT EXISTS
function_name AS "class_name" USING FILE "resource_locations" ;

-- Create a permanent function called `simple_udf`.
CREATE FUNCTION simple_udf AS 'SimpleUdf'
USING JAR '/tmp/SimpleUdf.jar' ;

-- Created a temporary function.
CREATE TEMPORARY FUNCTION simple_temp_udf AS 'SimpleUdf'
USING JAR '/tmp/SimpleUdf.jar' ;

-- Replace the implementation of `simple_udf`
CREATE OR REPLACE FUNCTION simple_udf AS 'SimpleUdfR'
USING JAR '/tmp/SimpleUdfR.jar' ;
