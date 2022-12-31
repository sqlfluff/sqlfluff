SELECT zoo.a
FROM foo AS zoo
{% if False %}
    WHERE zoo.datecol >= '2019-01-01'
{% endif %}
