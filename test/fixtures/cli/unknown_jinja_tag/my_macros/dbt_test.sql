{% test warn_if_odd(model, column_name) %}

    {{ config(severity = 'warn') }}

    select *
    from {{ model }}
    where ({{ column_name }} % 2) = 1

{% endtest %}
