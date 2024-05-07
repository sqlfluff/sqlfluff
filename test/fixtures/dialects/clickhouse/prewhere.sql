SELECT *
FROM table as t
PREWHERE event_date = 1;


SELECT *
FROM table as t
PREWHERE event_date = 1
ORDER BY t1;

SELECT *
FROM table as t
PREWHERE c1 = 1 AND c2 = 2
ORDER BY c1;

SELECT *
FROM table as t
PREWHERE c1 = 1 AND c2 = 2
WHERE c3 = 1
ORDER BY c1;


SELECT *
FROM table as t
PREWHERE c1 = 1 AND c2 = 2
GROUP BY c1
ORDER BY c1;
