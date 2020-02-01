-- Between and Not Between
-- https://github.com/alanmcruickshank/sqlfluff/issues/142
SELECT
    business_type
FROM
    benchmark_summaries
WHERE
    avg_click_rate NOT BETWEEN 0 and 1
    AND some_other_thing BETWEEN 0 and 1