{% set cols = ['c1', 'c2'] %}
{% set tables = ['t1', 't2'] %}

{% for (c, t) in zip(cols, tables) %}
select
  {{ c }} as col
from
  {{ t }}
{% if not loop.last %}
  union all
{% endif %}
{% endfor %}
