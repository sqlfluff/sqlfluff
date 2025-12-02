WITH
{% for i in [0, 1] %}
    {% if i == 0 %}
        cte0 AS (
            SELECT 1),
    {% else %}
        cte1 AS (
            SELECT 2)
    {% endif %}
{% endfor %}
SELECT * FROM cte0
UNION
SELECT * FROM cte1
