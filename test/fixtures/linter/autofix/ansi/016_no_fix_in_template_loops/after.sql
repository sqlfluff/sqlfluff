-- The second SELECT has parse errors (missing commas between the "columns").
-- This causes the "fixed" query to have weird indentation. The second SELECT's
-- main purpose is to ensure the loop body is not modified. (Issue 1425)
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
