-- Templated query aimed to stress the fixing templated sections.
SELECT
    foo,
    1+2+3+4+5 as bar1,
    1+{{test_expression_1}}+3 as bar2,
    1{{test_expression_2}}3 as bar3,
    {% if 1 == 0 %}
        {{test_expression_3}}
    {% endif %}
    foobar
FROM example_table
