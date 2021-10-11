SELECT
    `another-gcp-project.functions.timestamp_parsing`(log_tbl.orderdate) AS orderdate
FROM
    `gcp-project.data.year_2021` AS log_tbl
