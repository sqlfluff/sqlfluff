SELECT
    a
    {# My Comment #}
    , b
    {% for i in [1, 2, 3] %}
        , c_{{i}} + 42 AS the_meaning_of_li{{ 'f' * i }}
    {% endfor %}
    , boo
    {% for i in [1, 2, 3] %}
        , d_{{i}}
    {% endfor %}
FROM my_table
