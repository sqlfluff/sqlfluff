SELECT * EXCEPT ({% include query %}) FROM
    (
        SELECT
            tbl1.*,
            row_number()
                OVER (
                    PARTITION BY
                        tbl1.the_name, {{ context_columns | join(', ') }}
                    ORDER BY created_at DESC
                )
                AS rnk
        {% if context_columns | default("abc") == "abc" %}
            FROM tbl1
        {% endif %}
        INNER JOIN tbl2
            ON
                tbl1.the_name = tbl2.the_name
                AND tbl1.run_id = tbl2.run_id
        WHERE {{ run_rnk }} = {% include "foobar.sql" %}
    )
{% if +level - -level + level.level + level + level["key"] >= 0 %}
    WHERE rnk = 1
{% endif %}
