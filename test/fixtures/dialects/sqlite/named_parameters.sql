SELECT @variable
FROM table1
WHERE @variable = 1;

SELECT ?2
FROM table1
WHERE ?2 = 1;

SELECT :variable
FROM table1
WHERE :variable = 1;

SELECT $variable
FROM table1
WHERE $variable = 1;

SELECT @variable
FROM table1
GROUP BY @variable
HAVING $variable = 1;
