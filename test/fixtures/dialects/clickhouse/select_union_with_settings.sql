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
