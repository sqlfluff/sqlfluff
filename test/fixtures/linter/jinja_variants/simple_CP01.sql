-- sqlfluff:render_variant_limit:10
select 1 AS foo, {% if 1 > 2 %}2 AS boo{% else %}3 AS boo{% endif %}
