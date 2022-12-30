{% if True %}
SELECT 1
{% else %}
SELECT c
FROM t
WHERE c < 0
{% endif %}
