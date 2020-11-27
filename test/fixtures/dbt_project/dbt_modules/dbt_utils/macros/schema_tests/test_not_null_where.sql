{% macro test_not_null_where(model) %}

{% set column_name = kwargs.get('column_name', kwargs.get('arg')) %}
{% set where = kwargs.get('where', kwargs.get('arg')) %}

select count(*)
from {{ model }}
where {{ column_name }} is null
{% if where %} and {{ where }} {% endif %}

{% endmacro %}
