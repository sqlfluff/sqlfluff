-- Issue #2480
COPY (Select my_col From my_table) TO '/tmp/dump.csv' WITH (FORMAT csv, HEADER, DELIMITER '#', ENCODING 'UTF8');
COPY (Select * From my_table) TO '/tmp/dump.csv' WITH (FORMAT csv, HEADER, DELIMITER '#', NULL 'null', QUOTE '"');
COPY (Select * From my_table) TO '/tmp/dump.csv' WITH (FORMAT csv, ESCAPE '\', FREEZE true);
COPY (Select * From my_table) TO '/tmp/dump.csv' WITH (FORMAT csv, ESCAPE '\', FORCE_QUOTE (col1, col2));
COPY (Select * From my_table) TO '/tmp/dump.csv' WITH (FORMAT csv, ESCAPE '\', FORCE_QUOTE *);
COPY (Select * From my_table) TO '/tmp/dump.csv' WITH (FORMAT csv, ESCAPE '\', FORCE_NOT_NULL (col1, col2));
COPY (Select * From my_table) TO '/tmp/dump.csv' WITH (FORMAT csv, ESCAPE '\', FORCE_NULL (col1, col2), FREEZE false);
COPY (Select * From my_table) TO STDOUT WITH (FORMAT csv, ESCAPE '\', FORCE_NULL (col1, col2), FREEZE true);
COPY (Select * From my_table) TO PROGRAM '/path/to/script' WITH (FORMAT csv, ESCAPE '\', FORCE_NULL (col1, col2), FREEZE false);
COPY my_table(col) TO '/tmp/dump.csv';
COPY my_table TO '/tmp/dump.csv' WITH (FORMAT csv, HEADER true, FREEZE true, FORCE_NULL (col1, col2));
COPY my_table(col1, col2) TO '/tmp/dump.csv' WITH (FORMAT csv, HEADER true);
COPY my_table(col1, col2, col3, col4) TO PROGRAM '/path/to/script' WITH (FORMAT csv, HEADER true, FREEZE);
COPY my_table(col1, col2) TO STDOUT;
COPY my_table(col1, col2) TO STDOUT WITH (FORMAT csv, HEADER true, FREEZE false);
COPY my_table TO STDOUT WITH (FORMAT csv, HEADER true, FREEZE true, FORCE_NULL (col1, col2));

COPY my_table FROM '/tmp/dump.csv';
COPY my_table FROM STDIN;
COPY my_table FROM PROGRAM '/path/to/script';
COPY my_table(col) FROM '/tmp/dump.csv';
COPY my_table(col1, col2, col3) FROM STDIN;
COPY my_table(col1, col2) FROM PROGRAM '/path/to/script';

COPY my_table(col1, col2,col3, col4) FROM PROGRAM '/path/to/script' WITH (FORMAT csv, HEADER true, FREEZE true, FORCE_NULL (col1, col2));
COPY my_table(col1, col2,col3, col4) FROM '/tmp/dump.csv' WITH (FORMAT csv, ESCAPE '\', FORCE_QUOTE *);
COPY my_table FROM STDIN WITH (FORMAT csv, HEADER, DELIMITER '#', ENCODING 'UTF8');
COPY my_table FROM STDIN WITH (FORMAT csv, ESCAPE '\', FORCE_NULL (col1, col2), FREEZE true);
COPY my_table FROM STDIN WITH (FORMAT csv, HEADER, DELIMITER '#', NULL 'null', QUOTE '"', FORCE_QUOTE *);
COPY my_table FROM STDIN WITH (FORMAT csv, HEADER, DELIMITER '#', NULL 'null', QUOTE '"', FORCE_QUOTE *) WHERE col1 = 'some_value';
