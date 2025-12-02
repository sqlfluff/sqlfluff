WITH all_upstream_matches AS (
    SELECT
        ROW_NUMBER()
            OVER (
                PARTITION BY
                    low_business_type,
                    low_size_label,
                    low_gender_label,
                    low_age_label
                ORDER BY
                    business_type DESC,
                    size_label DESC,
                    gender_label DESC,
                    age_label DESC
            )
            AS rownum,
        business_type
    FROM
        acceptable_buckets
    JOIN
        small_buckets
    ON
        (business_type = low_business_type
            AND size_label = low_size_label
            AND gender_label = low_gender_label
            AND age_label = low_age_label)
)

SELECT
    business_type,
    user_counts
FROM
    acceptable_buckets
UNION ALL
SELECT
    business_type,
    user_counts
FROM
    substituted_buckets
