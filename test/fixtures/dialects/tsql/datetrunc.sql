SELECT DATETRUNC(YEAR, my_table.date) AS [beginningOfYear]
, DATETRUNC(MONTH, my_table.date) AS [FirstOfMonth]
, DATETRUNC(DAY, my_table.date) AS [Today]
FROM my_table;
