{% macro split_part(string_text, delimiter_text, part_number) %}
  {{ adapter.dispatch('split_part', packages = dbt_utils._get_utils_namespaces()) (string_text, delimiter_text, part_number) }}
{% endmacro %}


{% macro default__split_part(string_text, delimiter_text, part_number) %}

    split_part(
        {{ string_text }},
        {{ delimiter_text }},
        {{ part_number }}
        )

{% endmacro %}


{% macro bigquery__split_part(string_text, delimiter_text, part_number) %}

    split(
        {{ string_text }},
        {{ delimiter_text }}
        )[safe_offset({{ part_number - 1 }})]

{% endmacro %}
