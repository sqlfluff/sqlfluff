{% if True %}
SELECT 1
{% else %}
{% if True %}
SELECT 2
{% else %}
SELECT 3
{% endif %}
{% endif %}
