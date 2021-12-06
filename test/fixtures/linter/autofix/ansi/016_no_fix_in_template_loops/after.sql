-- The second and third SELECTs have parse errors, causing weird indentation.
-- Not that concerned because the main purpose of this test case is to ensure
-- "sqlfluff fix" does not make changes inside the loop body. (Issue 1425)
SELECT
    {% for _ in [1, 2, 3] %} 2,
 {% endfor %}
    10;

SELECT
    1,
    {%- for _ in [1, 2, 3] %}    2{%endfor %};

SELECT
    1,
    {% for _ in [1, 2, 3] %}    2{%endfor %}
