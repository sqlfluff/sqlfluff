SELECT
    user_id
FROM
    `project.dataset.table1`
    FOR SYSTEM_TIME AS OF CAST('2020-05-11T14:02:52+00:00' AS TIMESTAMP)