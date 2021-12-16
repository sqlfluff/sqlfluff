-- Unexpected Join Fail
-- https://github.com/sqlfluff/sqlfluff/issues/163
SELECT
    data.id
FROM
    data
JOIN
    data_max
ON
    data.event_id = data_max.event_id
LEFT JOIN
    "other_db"."other_data" AS od
ON
    od.fid = data_max.fid
