{% if True %}
SELECT 1
{% elif True %}
SELECT {{ 1 + "2" }}
{% else %}
SELECT 2
{% endif %}
