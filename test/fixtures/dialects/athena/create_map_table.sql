CREATE TABLE map_table(c1 map<string, integer>) LOCATION '...';
INSERT INTO map_table values(MAP(ARRAY['foo', 'bar'], ARRAY[1, 2]));
