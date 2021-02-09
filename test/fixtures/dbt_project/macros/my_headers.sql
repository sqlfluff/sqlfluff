-- Issue #516
{% macro my_headers() %}
    -- Materialization: {{ config.get('materialization') }}
{% endmacro %}
