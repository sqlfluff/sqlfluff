COPY "schema_1"."table_1" ("field_1", )
FROM STDIN
WITH CSV
NULL ''
DELIMITER '	'
ESCAPE '\\'
;

COPY country TO STDOUT (DELIMITER '|');

COPY country FROM '/home/usr1/sql/country_data';

COPY (SELECT * FROM country WHERE country_name LIKE 'A%') TO
'/home/usr1/sql/a_list_countries.copy';

COPY sales FROM '/home/usr1/sql/sales_data' LOG ERRORS
   SEGMENT REJECT LIMIT 10 ROWS;

COPY mytable TO '<SEG_DATA_DIR>/gpbackup<SEGID>.txt' ON SEGMENT;

COPY (SELECT * FROM testtbl) TO '/tmp/mytst<SEGID>' ON SEGMENT;

COPY LINEITEM TO PROGRAM 'cat > /tmp/lineitem.csv' CSV;

COPY LINEITEM_4 FROM PROGRAM 'cat /tmp/lineitem_program<SEGID>.csv' ON SEGMENT CSV;

COPY table_name FROM '/path/to/file.csv' DELIMITER ',' CSV HEADER;

COPY schema_name.table_name FROM '/path/to/file.csv' DELIMITER ';' CSV HEADER;

COPY table_name (column1, column2, column3) FROM '/path/to/file.csv' DELIMITER ',' CSV HEADER;

COPY table_name FROM PROGRAM 'cat /path/to/file.csv' DELIMITER ',' CSV HEADER;

COPY table_name FROM '/path/to/file.csv' DELIMITER ',' CSV QUOTE '"' ESCAPE '';

COPY table_name FROM '/path/to/file.csv' DELIMITER ',' CSV NULL 'NA' HEADER;

COPY table_name (column1, column2, column3) FROM '/path/to/file.csv' DELIMITER ',' CSV HEADER QUOTE '"';

COPY table_name FROM '/path/to/file.csv' DELIMITER ',' CSV ESCAPE '';

COPY table_name FROM '/path/to/file.csv' DELIMITER ',' CSV HEADER ENCODING 'UTF8';
