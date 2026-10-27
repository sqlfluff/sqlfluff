CREATE FUNCTION my_udf AS 'com.example.Udf';

CREATE TEMPORARY FUNCTION IF NOT EXISTS my_udf AS 'com.example.Udf' LANGUAGE JAVA;

CREATE TEMPORARY SYSTEM FUNCTION IF NOT EXISTS my_udf AS 'com.example.Udf';

CREATE FUNCTION my_udf AS 'com.example.Udf' LANGUAGE SCALA USING JAR 'file:///opt/lib/a.jar', JAR 'file:///opt/lib/b.jar';

CREATE FUNCTION my_udf AS 'com.example.Udf' USING ARTIFACT 's3://bucket/a.jar' WITH ('k' = 'v');
