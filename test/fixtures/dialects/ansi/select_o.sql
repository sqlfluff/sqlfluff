-- Between and Not Between
-- https://github.com/sqlfluff/sqlfluff/issues/142
-- https://github.com/sqlfluff/sqlfluff/issues/478
-- https://github.com/sqlfluff/sqlfluff/issues/2845
SELECT
    business_type
FROM
    benchmark_summaries
WHERE
    avg_click_rate NOT BETWEEN 0 and 1 + 1 + some_value
    AND some_other_thing BETWEEN 0 - 1 * another_value and 1
    AND another_thing BETWEEN -another_value and 0
