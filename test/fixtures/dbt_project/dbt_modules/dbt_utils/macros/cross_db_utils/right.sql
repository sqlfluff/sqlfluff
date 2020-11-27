{% macro right(string_text, length_expression) -%}
    {{ adapter.dispatch('right', packages = dbt_utils._get_utils_namespaces()) (string_text, length_expression) }}
{% endmacro %}

{% macro default__right(string_text, length_expression) %}

    right(
        {{ string_text }},
        {{ length_expression }}
    )
    
{%- endmacro -%}

{% macro bigquery__right(string_text, length_expression) %}

    case when {{ length_expression }} = 0 
        then ''
    else 
        substr(
            {{ string_text }},
            -1 * ({{ length_expression }})
        )
    end

{%- endmacro -%}

{% macro snowflake__right(string_text, length_expression) %}

    case when {{ length_expression }} = 0 
        then ''
    else 
        right(
            {{ string_text }},
            {{ length_expression }}
        )
    end

{%- endmacro -%}