SELECT
    `another-gcp-project`.`functions.timestamp_parsing` (log_tbl.first_move) AS first_move
FROM
    `gcp-project.data.year_2021` AS log_tbl
