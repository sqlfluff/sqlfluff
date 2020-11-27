{% macro except() %}
  {{ adapter.dispatch('except', packages = dbt_utils._get_utils_namespaces())() }}
{% endmacro %}


{% macro default__except() %}

    except

{% endmacro %}
    
{% macro bigquery__except() %}

    except distinct

{% endmacro %}