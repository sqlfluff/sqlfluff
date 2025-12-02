select
  0,
  {% for i in [1, 2, 3] %}
    i,
  {% endfor %}
  4