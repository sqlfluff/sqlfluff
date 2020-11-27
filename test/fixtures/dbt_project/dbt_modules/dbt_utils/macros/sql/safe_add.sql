{%- macro safe_add() -%}

{% set fields = [] %}

{%- for field in varargs -%}

    {% do fields.append("coalesce(" ~ field ~ ", 0)") %}

{%- endfor -%}

{{ fields|join(' +\n  ') }}

{%- endmacro -%}
