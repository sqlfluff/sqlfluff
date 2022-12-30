SELECT c1, c2 FROM t1 WHERE
{% if True %}
1 = 1
{% else %}
EXISTS(SELECT * FROM t2 WHERE t1.c1 = t2.c1)
{% endif %}

