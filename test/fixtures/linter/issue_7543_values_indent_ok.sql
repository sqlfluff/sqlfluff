WITH cte_example (col1, col2) AS (
  SELECT
    $1
    , $2
  FROM (
    VALUES
    ('value1', 'value2')
  )
)

SELECT * FROM cte_example;
