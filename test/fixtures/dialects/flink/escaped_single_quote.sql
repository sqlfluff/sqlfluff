SELECT 'it''s a string';

CREATE TABLE my_table (
    id INT
) WITH (
    'connector' = 'kafka',
    'query' = 'SELECT ''a'' FROM my_table WHERE b = ''c'''
);
