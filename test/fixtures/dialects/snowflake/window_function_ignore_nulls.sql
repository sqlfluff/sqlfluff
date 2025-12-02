 SELECT
  FIRST_VALUE(foo) IGNORE NULLS over (
              PARTITION BY buzz
              ORDER BY bar
              ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS bat
            from some_table
