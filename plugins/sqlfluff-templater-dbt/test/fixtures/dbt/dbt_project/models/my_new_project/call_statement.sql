{% call statement('unique_keys', fetch_result=True) %}
  select 'tests' as key_name
{% endcall %}
{% set unique_keys = load_result('unique_keys') %}
select 1, '{{ unique_keys.data[0][0] }}'
