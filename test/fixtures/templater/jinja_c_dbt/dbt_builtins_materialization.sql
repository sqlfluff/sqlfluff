{% materialization my_view, adapter='snowflake' %}
{%- set target_relation = this.incorporate(type='view') -%}
{% call statement('main') -%}
SELECT 1 AS a
{%- endcall %}
{{ return({'relations': [target_relation]}) }}
{% endmaterialization %}
-- no sql produced
