-- NOTE: This query is duplicated many times so the test
-- takes longer and can effectively measure timing routines.

{% for i in range(10) %}
    SELECT
        tbl.name,
        b.value,
        /*
        This is a block comment
        */
        d.something,    -- Which a comment after it
        tbl.foo,
        d.val + b.val / -2 AS a_calculation
    FROM tbl
    INNER JOIN b ON (tbl.common_id = b.common_id)
    LEFT JOIN d ON (tbl.id = d.other_id)
    ORDER BY tbl.name ASC;
{% endfor %}
