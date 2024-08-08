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

COPY copy_statement_bug FROM stdin WITH csv header;
COPY my_table FROM STDIN WITH;
COPY my_table FROM STDIN WITH BINARY;
COPY my_table FROM STDIN WITH DELIMITER '#';
COPY my_table FROM STDIN WITH DELIMITER AS '#';
COPY my_table FROM STDIN WITH NULL 'null';
COPY my_table FROM STDIN WITH NULL AS 'null';
COPY my_table FROM STDIN WITH CSV;
COPY my_table FROM STDIN WITH CSV QUOTE '"';
COPY my_table FROM STDIN WITH CSV QUOTE AS '"';
COPY my_table FROM STDIN WITH CSV ESCAPE '\';
COPY my_table FROM STDIN WITH CSV ESCAPE AS '\';
COPY my_table FROM STDIN WITH CSV FORCE NOT NULL col1;
COPY my_table FROM STDIN WITH CSV FORCE NOT NULL col1, col2;

COPY my_table FROM '/tmp/dump.csv' WITH BINARY;
COPY my_table FROM '/tmp/dump.csv' WITH DELIMITER '#';
COPY my_table FROM '/tmp/dump.csv' WITH DELIMITER AS '#';
COPY my_table FROM '/tmp/dump.csv' WITH NULL 'null';
COPY my_table FROM '/tmp/dump.csv' WITH NULL AS 'null';
COPY my_table FROM '/tmp/dump.csv' WITH CSV;
COPY my_table FROM '/tmp/dump.csv' WITH CSV QUOTE '"';
COPY my_table FROM '/tmp/dump.csv' WITH CSV QUOTE AS '"';
COPY my_table FROM '/tmp/dump.csv' WITH CSV ESCAPE '\';
COPY my_table FROM '/tmp/dump.csv' WITH CSV ESCAPE AS '\';

COPY (SELECT * FROM country WHERE country_name LIKE 'A%') TO '/usr1/proj/bray/sql/a_list_countries.copy';
COPY my_table(col1, col2) TO STDOUT;
COPY my_table(col2) TO STDOUT;
COPY my_table(col1, col2) TO STDOUT WITH;
COPY my_table(col1, col2) TO STDOUT WITH BINARY;
COPY my_table(col1, col2) TO STDOUT WITH DELIMITER '#';
COPY my_table(col1, col2) TO STDOUT WITH DELIMITER AS '#';
COPY my_table TO STDOUT WITH NULL 'null';
COPY my_table TO STDOUT WITH NULL AS 'null';

COPY my_table(col1) TO STDOUT WITH CSV;
COPY my_table TO STDOUT WITH CSV HEADER;
COPY my_table TO STDOUT WITH CSV QUOTE '"';
COPY my_table TO STDOUT WITH CSV QUOTE AS '"';
COPY my_table TO STDOUT WITH CSV ESCAPE '\';
COPY my_table(col1, col2) TO STDOUT WITH CSV ESCAPE AS '\';
COPY my_table(col1, col2) TO STDOUT WITH CSV FORCE QUOTE *;
COPY my_table(col1, col2) TO STDOUT WITH CSV FORCE QUOTE (col1, col2);
