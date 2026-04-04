SELECT * FROM test1
UNION ALL
SELECT * FROM test2
SETTINGS allow_experimental_window_functions = 1;

SELECT * FROM test1
UNION ALL
SELECT * FROM test2
UNION ALL
SELECT * FROM test3
SETTINGS max_threads = 4, allow_experimental_window_functions = 1;

-- FORMAT after UNION ALL
SELECT * FROM test1
UNION ALL
SELECT * FROM test2
FORMAT CSV;

-- INTO OUTFILE after UNION ALL
SELECT * FROM test1
UNION ALL
SELECT * FROM test2
INTO OUTFILE 'output.csv' FORMAT CSV;

SELECT 1
UNION ALL
SELECT 2
SETTINGS max_threads = 1
INTO OUTFILE 'output.csv'
