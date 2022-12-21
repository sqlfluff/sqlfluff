select 1
{% if target.database == 'test' -%}
  union all
  select 2
{%- endif -%}
