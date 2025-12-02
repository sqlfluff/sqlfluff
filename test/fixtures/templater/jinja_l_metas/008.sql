{% for item in [1,2] -%}
SELECT *
FROM some_table
{{ "UNION ALL\n" if not loop.last }}
{%- endfor %}