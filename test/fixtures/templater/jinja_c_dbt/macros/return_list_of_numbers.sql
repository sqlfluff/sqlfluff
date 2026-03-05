{% macro return_list_of_numbers() %}
  {% do return([1, 2, 3]) %}
{% endmacro %}
