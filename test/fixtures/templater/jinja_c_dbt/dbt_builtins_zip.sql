{% set not_iterable = 1 %}
{% set iterable = ['a1', 'a2'] %}
{% set result = zip(not_iterable, iterable) %}

select
  {{ result }}
