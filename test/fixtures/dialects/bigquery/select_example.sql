-- This query should also parse in ANSI, but as a bigquery example
-- it probably lives here. In particular it has an un-bracketed
-- select clause within a function, and array notation which
-- makes it a useful test case.
WITH age_buckets_bit_array AS (
    SELECT
      bucket_id,
      num_ranges,
      min_age,
      ARRAY(SELECT CAST(num AS INT64) FROM UNNEST(SPLIT(binary, '')) AS num) AS bits,
      age_label
    FROM
      age_buckets
  ),
  bucket_abundance AS (
    SELECT
      bucket_id
      (count_18_24 * bits[OFFSET(0)] + count_25_34 * bits[OFFSET(1)] +
       count_35_44 * bits[OFFSET(2)] + count_45_54 * bits[OFFSET(3)] +
       count_55_64 * bits[OFFSET(4)] + count_65_plus * bits[OFFSET(5)]) / audience_size AS relative_abundance
    FROM
      audience_counts_gender_age
    CROSS JOIN
      age_buckets_bit_array
  )

SELECT
  *
FROM
  age_buckets_bit_array
JOIN
  bucket_abundance
USING (bucket_id)
