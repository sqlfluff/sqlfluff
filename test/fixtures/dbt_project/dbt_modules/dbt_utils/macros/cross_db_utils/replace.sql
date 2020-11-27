{% macro replace(field, old_chars, new_chars) -%}
    {{ adapter.dispatch('replace', packages = dbt_utils._get_utils_namespaces()) (field, old_chars, new_chars) }}
{% endmacro %}


{% macro default__replace(field, old_chars, new_chars) %}

    replace(
        {{ field }},
        {{ old_chars }},
        {{ new_chars }}
    )
    

{% endmacro %}