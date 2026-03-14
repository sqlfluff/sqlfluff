-- Standard SQL form
SELECT SUM(x) FILTER (WHERE y > 0);

-- DuckDB (WHERE optional)
SELECT SUM(x) FILTER (y > 0);

-- Example on documentation page
SELECT
    sum(i) FILTER (i <= 5) AS lte_five_sum,
    median(i) FILTER (i % 2 = 1) AS odds_median,
    median(i) FILTER (i % 2 = 1 AND i <= 5) AS odds_lte_five_median
FROM generate_series(1, 10) tbl(i);
