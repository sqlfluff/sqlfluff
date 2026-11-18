SELECT *
FROM my_table AS t
CROSS JOIN LATERAL TABLE(my_table_function(t.payload)) AS p (item);

SELECT *
FROM my_table AS t,
LATERAL TABLE(my_table_function(t.payload)) AS p (item);
