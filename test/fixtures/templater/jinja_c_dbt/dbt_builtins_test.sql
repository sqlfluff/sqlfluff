{% test my_cool_test(model, column_name, kwarg1=none, kwarg2=none) %}
SELECT {{ column_name }} FROM {{ model }}
WHERE thing = 1
{% if kwarg1 %}
AND otherthing = 2
{% endif %}
{% if kwarg2 %}
AND anotherthing = 3
{% endif %}
{% endtest %}
-- no sql produced
