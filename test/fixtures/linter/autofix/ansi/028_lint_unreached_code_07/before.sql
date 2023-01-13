SELECT c1
  FROM table_a
{% if False %}
    INNER JOIN table_b USING (id)
    WHERE table_b.datecol >= '2019-01-01'
{% endif %}
