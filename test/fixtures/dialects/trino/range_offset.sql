-- https://trino.io/blog/2021/03/10/introducing-new-window-features.html

SELECT
    student_id,
    result,
    count(*) OVER (
        ORDER BY result
        RANGE BETWEEN 1 FOLLOWING AND 2 FOLLOWING) AS close_better_scores_count
FROM students_results;

SELECT avg(totalprice) OVER (
    PARTITION BY custkey
    ORDER BY orderdate
    RANGE BETWEEN interval '1' DAY PRECEDING AND interval '1' DAY FOLLOWING)
FROM orders;

SELECT
	avg(totalprice) OVER w,
	sum(totalprice) OVER w,
	max(totalprice) OVER w
FROM orders
WINDOW w AS (
    PARTITION BY custkey
    ORDER BY orderdate
    RANGE BETWEEN interval '1' month PRECEDING AND CURRENT ROW)
