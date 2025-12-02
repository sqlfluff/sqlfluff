-- This file combines product data from individual brands into a staging table
{% set products =  [
  'table1',
  'table2'] %}

{% for product in products %}
    SELECT
        brand,
        country_code,
        category,
        name,
        id
    FROM
        {{ product }}
    {% if not loop.last -%} UNION ALL {%- endif %}
{% endfor %}
