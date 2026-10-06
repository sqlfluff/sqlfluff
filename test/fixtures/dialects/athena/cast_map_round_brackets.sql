SELECT CAST(JSON_PARSE('{"key": "value"}') AS MAP(varchar, varchar));
SELECT CAST(c1 AS MAP(varchar, varchar)) FROM map_table;
SELECT CAST(c1 AS ARRAY(MAP(varchar, varchar))) FROM map_table;
SELECT CAST(c1 AS MAP(varchar, ARRAY(integer))) FROM map_table;
