{#
This macro fetches the unique values for `column` in the table `table`

Arguments:
    table: A model `ref`, or a schema.table string for the table to query (Required)
    column: The column to query for unique values
    max_records: If provided, the maximum number of unique records to return (default: none)

Returns:
    A list of distinct values for the specified columns
#}

{% macro get_column_values(table, column, max_records=none, default=none) -%}

{#-- Prevent querying of db in parsing mode. This works because this macro does not create any new refs. #}
    {%- if not execute -%}
        {{ return('') }}
    {% endif %}
{#--  #}

    {%- set target_relation = adapter.get_relation(database=table.database,
                                          schema=table.schema,
                                         identifier=table.identifier) -%}

    {%- call statement('get_column_values', fetch_result=true) %}

        {%- if not target_relation and default is none -%}

          {{ exceptions.raise_compiler_error("In get_column_values(): relation " ~ table ~ " does not exist and no default value was provided.") }}

        {%- elif not target_relation and default is not none -%}

          {{ log("Relation " ~ table ~ " does not exist. Returning the default value: " ~ default) }}

          {{ return(default) }}

        {%- else -%}

            select
                {{ column }} as value

            from {{ target_relation }}
            group by 1
            order by count(*) desc

            {% if max_records is not none %}
            limit {{ max_records }}
            {% endif %}

        {% endif %}

    {%- endcall -%}

    {%- set value_list = load_result('get_column_values') -%}

    {%- if value_list and value_list['data'] -%}
        {%- set values = value_list['data'] | map(attribute=0) | list %}
        {{ return(values) }}
    {%- else -%}
        {{ return(default) }}
    {%- endif -%}

{%- endmacro %}
