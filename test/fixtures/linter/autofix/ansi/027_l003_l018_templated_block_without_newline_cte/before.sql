WITH
{% if true %}
    cte AS (
        SELECT 1)
{% else %}
    cte AS (
        SELECT 2)
{% endif %}
SELECT * FROM cte
