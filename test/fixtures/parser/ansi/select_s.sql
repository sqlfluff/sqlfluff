-- Array notation (BigQuery and Postgres)
-- https://github.com/sqlfluff/sqlfluff/issues/59
SELECT
  user_id,
  list_id,
  (count_18_24 * bits[OFFSET(0)] + count_25_34 * bits[OFFSET(1)] +
   count_35_44 * bits[OFFSET(2)] + count_45_54 * bits[OFFSET(3)] +
   count_55_64 * bits[OFFSET(4)] + count_65_plus * bits[OFFSET(5)]) / audience_size AS relative_abundance
FROM
    gcp_project.dataset.audience_counts_gender_age
