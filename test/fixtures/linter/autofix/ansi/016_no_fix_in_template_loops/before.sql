SELECT
{% for _ in [1, 2, 3] %} 2,
{% endfor %}
    10;

SELECT
    1,
  {% for _ in [1, 2, 3] %}    2{%endfor %}
