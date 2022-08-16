{% macro sb_incremental(tbl, source, tbl_id='match_id', source_id='match_id') %}

  {% if is_incremental() %}

    (
      select
        *
      from {{ source }} as s
      where (
        s.{{ source_id }} not in (select distinct {{ tbl_id }} from {{ tbl.name }})
      )
    )

  {% else %}

  {{ source }}

  {% endif %}

{% endmacro %}
