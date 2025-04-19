-- JOIN should not be parsed as nested in OUTER APPLY
SELECT table1.*
FROM table1
OUTER APPLY table2
INNER JOIN table3
    ON table1.col = table3.col
WHERE table1.Column1 ='blah';
