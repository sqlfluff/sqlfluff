{% set cols = ['c1', 'c2'] %}
{% set aliases = ['a1', 'a2'] %}

select
{% for (col, alias) in zip_strict(cols, aliases) %}
  {{ col }} as {{ alias }}{% if not loop.last %},{% endif %}
{% endfor %}
