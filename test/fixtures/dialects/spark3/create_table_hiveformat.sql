--Create Hiveformat Table with all optional syntax
CREATE EXTERNAL TABLE IF NOT EXISTS table_identifier
( col_name1 STRING COMMENT "col_comment1")
COMMENT "table_comment"
PARTITIONED BY ( col_name2 STRING COMMENT "col_comment2" )
CLUSTERED BY ( col_name1, col_name2)
SORTED BY ( col_name1 ASC, col_name2 DESC )
INTO 3 BUCKETS
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS PARQUET
LOCATION "path/to/files"
TBLPROPERTIES ( "key1" = "val1", "key2" = "val2")
AS (SELECT * FROM table_identifier);

--Use hive format
CREATE TABLE student (id INT, student_name STRING, age INT) STORED AS ORC;

--Use data from another table
CREATE TABLE student_copy STORED AS ORC
AS SELECT * FROM student;

--Specify table comment and properties
CREATE TABLE student (id INT, student_name STRING, age INT)
COMMENT 'this is a comment'
STORED AS ORC
TBLPROPERTIES ('foo' = 'bar');

--Specify table comment and properties with different clauses order
CREATE TABLE student (id INT, student_name STRING, age INT)
STORED AS ORC
TBLPROPERTIES ('foo' = 'bar')
COMMENT 'this is a comment';

--Create partitioned table
CREATE TABLE student (id INT, student_name STRING)
PARTITIONED BY (age INT)
STORED AS ORC;

--Create partitioned table with different clauses order
CREATE TABLE student (id INT, student_name STRING)
STORED AS ORC
PARTITIONED BY (age INT);

--Use Row Format and file format
CREATE TABLE student (id INT, student_name STRING)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE;

--Use complex datatype
CREATE EXTERNAL TABLE family(
    student_name STRING,
    friends ARRAY<STRING>,
    children MAP<STRING, INT>,
    address STRUCT<street: STRING, city: STRING>
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' ESCAPED BY '\\'
COLLECTION ITEMS TERMINATED BY '_'
MAP KEYS TERMINATED BY ':'
LINES TERMINATED BY '\n'
NULL DEFINED AS 'foonull'
STORED AS TEXTFILE
LOCATION '/tmp/family/';

--Use predefined custom SerDe
CREATE TABLE avroexample
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.avro.AvroSerDe'
STORED AS INPUTFORMAT
'org.apache.hadoop.hive.ql.io.avro.AvroContainerInputFormat'
OUTPUTFORMAT
'org.apache.hadoop.hive.ql.io.avro.AvroContainerOutputFormat'
TBLPROPERTIES (
    'avro.schema.literal' =
    '{
        "namespace": "org.apache.hive",
        "name": "first_schema",
        "type": "record",
        "fields": [ { "name":"string1", "type":"string" }, { "name":"string2", "type":"string" }]
    }'
);

--Use personalized custom SerDe
--(we may need to `ADD JAR xxx.jar` first to ensure we can find the serde_class,
--or you may run into `CLASSNOTFOUND` exception)
ADD JAR '/tmp/hive_serde_example.jar';

CREATE EXTERNAL TABLE family (id INT, family_name STRING)
ROW FORMAT SERDE 'com.ly.spark.serde.SerDeExample'
STORED AS INPUTFORMAT 'com.ly.spark.example.serde.io.SerDeExampleInputFormat'
OUTPUTFORMAT 'com.ly.spark.example.serde.io.SerDeExampleOutputFormat'
LOCATION '/tmp/family/';

--Use `CLUSTERED BY` clause to create bucket table without `SORTED BY`
CREATE TABLE clustered_by_test1 (id INT, age STRING)
CLUSTERED BY (id)
INTO 4 BUCKETS
STORED AS ORC;

--Use `CLUSTERED BY` clause to create bucket table with `SORTED BY`
CREATE TABLE clustered_by_test2 (id INT, test_name STRING)
PARTITIONED BY (test_year STRING)
CLUSTERED BY (id, name)
SORTED BY (id ASC)
INTO 3 BUCKETS
STORED AS PARQUET;
