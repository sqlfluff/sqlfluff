WITH audience_counts AS (
    SELECT
        user_id,
        list_id,
        COUNT(email_id) AS audience
    FROM
        lists_emails AS list_emails
    WHERE
        list_emails.active != 'D'
    GROUP BY
        user_id,
        list_id
)

SELECT
    user_id,
    list_id,
    audience,
    CASE
        WHEN audience > 0 AND audience <= 200 THEN '< 200'
        WHEN
            audience > 200
            AND audience <= 3000
            -- NB: This one is a hanging indent, which should be modified.
            AND audience <= 2000 THEN '200 - 2,000'
        WHEN audience > 2000 AND audience <= 10000 THEN '2,000 - 10,000'
        WHEN
            audience > 10000
            AND audience <= 50000 THEN '10,000 - 50,000'
        WHEN audience > 50000 AND audience <= 500000 THEN '50,000 - 500,000'
        WHEN audience > 500000 THEN '> 500,000'
    END AS size_bucket
FROM
    audience_counts
JOIN
    gdpr_safe_users
    USING
        (user_id)
