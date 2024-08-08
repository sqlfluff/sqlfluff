SELECT replace(some_field, e'\r\n', ', ')
FROM table_name;

SELECT replace(some_field, E'\r\n', ', ')
FROM table_name;

SELECT E'\'';

SELECT E'''';

SELECT E'''\'';

SELECT E'\\\'''';

SELECT E'

\\
''
\\';
