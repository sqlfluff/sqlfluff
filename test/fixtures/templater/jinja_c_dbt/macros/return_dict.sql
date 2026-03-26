{% macro return_dict() %}
  {% do return({"hello": "world"}) %}
{% endmacro %}
