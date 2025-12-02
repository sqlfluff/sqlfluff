CREATE TABLE student (id INT, student_name STRING, age INT)
    TBLPROPERTIES (delta.enableChangeDataFeed = true);

ALTER TABLE my_delta_table
    SET TBLPROPERTIES (delta.enableChangeDataFeed = true);

SET spark.databricks.delta.properties.defaults.enableChangeDataFeed = true;
