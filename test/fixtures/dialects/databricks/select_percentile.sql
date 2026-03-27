-- Test PERCENTILE_CONT with WITHIN GROUP clause
SELECT percentile_cont(array(0.5, 0.4, 0.1)) WITHIN GROUP (ORDER BY col)
FROM VALUES (0), (1), (2), (10) AS tab(col);

-- Test PERCENTILE_DISC with WITHIN GROUP clause
SELECT percentile_disc(0.5) WITHIN GROUP (ORDER BY col)
FROM VALUES (0), (1), (2), (10) AS tab(col);

-- Test with multiple percentiles and aliases
SELECT
    col_group,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY measure ASC) AS median_measure,
    percentile_cont(0.9) WITHIN GROUP (ORDER BY measure DESC) AS p90_measure
FROM some_table
GROUP BY col_group;
