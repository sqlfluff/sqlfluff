SELECT
    apple,
    {% for num in ('1') %}
        CASE WHEN {{ num }} = 1 THEN cool ELSE moo END AS col_{{ num }}
    {% endfor %}
    , pear
FROM fruit
