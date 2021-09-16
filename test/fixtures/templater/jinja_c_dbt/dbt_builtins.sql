{{ config(blah=60) }}

SELECT
    col1,
    col2
FROM {{ ref('my_table') }}
