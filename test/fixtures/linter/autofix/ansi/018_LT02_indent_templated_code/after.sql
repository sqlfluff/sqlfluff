-- This file combines product data from individual brands into a staging table
{% set products =  ['table1'] %}

{% for product in products %}
    SELECT
        brand,
        country_code
    FROM
        {{ product }}
    {% if not loop.last -%} UNION ALL {%- endif %}
{% endfor %}
