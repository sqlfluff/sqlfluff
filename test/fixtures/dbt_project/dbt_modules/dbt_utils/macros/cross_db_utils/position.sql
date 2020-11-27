{% macro position(substring_text, string_text) -%}
    {{ adapter.dispatch('position', packages = dbt_utils._get_utils_namespaces()) (substring_text, string_text) }}
{% endmacro %}


{% macro default__position(substring_text, string_text) %}

    position(
        {{ substring_text }} in {{ string_text }}
    )
    
{%- endmacro -%}

{% macro bigquery__position(substring_text, string_text) %}

    strpos(
        {{ string_text }},
        {{ substring_text }}
        
    )
    
{%- endmacro -%}
