-- redshift_pivot.sql
/* Examples of SELECT statements that include PIVOT clauses. */

SELECT *
FROM (SELECT partname, price FROM part) PIVOT (
    AVG(price) FOR partname IN ('P1', 'P2', 'P3')
);
