{%- if false -%}
(
  SELECT
    *
  FROM
    {{ "t1" }}
  WHERE
  {# basic incremental logic goes here. I don't think this is the issue. #}
        datecol >= '2019-01-01'
)
{%- else -%}
    (
        SELECT * FROM {{ "t1" }}
    )
{%- endif -%}


