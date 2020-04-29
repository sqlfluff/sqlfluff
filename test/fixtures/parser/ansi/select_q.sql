-- Unexpected Join Fail
-- https://github.com/alanmcruickshank/sqlfluff/issues/163
SELECT
    data1.id1
FROM
    data1
JOIN
    data_max
ON
    data1.event_id = data_max.event_id
LEFT JOIN
    "other_db"."other_data" AS od
ON
    od.fid = data_max.fid