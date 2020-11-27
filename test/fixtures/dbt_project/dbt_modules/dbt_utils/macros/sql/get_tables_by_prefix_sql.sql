{% macro get_tables_by_prefix_sql(schema, prefix, exclude='', database=target.database) %}
    
    {{ dbt_utils.get_tables_by_pattern_sql(
        schema_pattern = schema,
        table_pattern = prefix ~ '%',
        exclude = exclude,
        database = database
    ) }}
    
{% endmacro %}
