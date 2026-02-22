\copy mytable FROM '/path/to/file.csv' WITH (FORMAT csv, HEADER true);

\copy mytable TO STDOUT;

\copy (SELECT id, name FROM mytable WHERE active = true) TO '/path/to/out.csv' CSV HEADER;

\copy (
    SELECT id, name
    FROM mytable
    WHERE active = true
) TO '/path/to/out.csv' CSV HEADER;

\copy table_name(col1, col2) FROM STDIN CSV;

SELECT 1;
