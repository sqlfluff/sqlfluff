{%- set evens = [] -%}
{%- for x in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] -%}
    {%- if x % 2 == 0 -%}
        {%- do evens.append(x) -%}
    {%- endif -%}
{%- endfor -%}

select
    {% for x in evens -%}
        {{ x }} as {{ 'col' ~ x }}
        {%- if not loop.last -%}, {% endif %}
    {% endfor -%}
