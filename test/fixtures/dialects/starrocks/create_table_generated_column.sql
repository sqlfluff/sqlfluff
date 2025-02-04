CREATE TABLE test_tbl1
(
    id INT NOT NULL,
    data_array ARRAY NOT NULL,
    data_json JSON NOT NULL,
    newcol1 DOUBLE AS array_avg(data_array),
    newcol2 String AS json_string(json_query(data_json, "$.a"))
)
PRIMARY KEY (id)
DISTRIBUTED BY HASH(id);
