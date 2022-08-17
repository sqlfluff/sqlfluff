{% include query %}
SELECT * EXCEPT(rnk) FROM
    (
        SELECT
            tbl1.*,
            row_number() OVER (
                PARTITION BY
                    tbl1.the_name, {{ context_columns | join(', ') }}
                ORDER BY created_at DESC
            ) AS rnk
        FROM tbl1
        INNER JOIN tbl2
            ON tbl1.the_name = tbl2.the_name
                AND tbl1.run_id = tbl2.run_id
        WHERE {{ run_rnk }} = 1
    )
{% if level.level + level >= 0 %}
    WHERE rnk = 1
{% endif %}
