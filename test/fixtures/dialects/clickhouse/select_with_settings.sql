SELECT * FROM test1
SETTINGS allow_experimental_window_functions = 1;

SELECT * FROM test1
WHERE a = ''
SETTINGS allow_experimental_window_functions = 1;

SELECT * FROM test1
ORDER BY 2
SETTINGS allow_experimental_window_functions = 1;
