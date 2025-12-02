CREATE TABLE struct_table(c1 struct<name:varchar(10), age:integer>) LOCATION '...';

INSERT INTO struct_table SELECT CAST(ROW('Bob', 38) AS ROW(name VARCHAR(10), age INTEGER));
