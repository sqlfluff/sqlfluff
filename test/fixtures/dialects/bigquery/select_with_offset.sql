-- This has a table expression and also an offset value.
-- It also includes a nested SELECT
SELECT SUM(CASE WHEN value != previous_value THEN 1.0 ELSE 0.0 END)
      FROM (
        SELECT
          value,
          CASE WHEN ix != 0 THEN LAG(value) OVER (ORDER BY ix ASC) ELSE value END AS previous_value
        FROM UNNEST(sequence_validation_and_business_rules.sequence_validation_and_business_rules) AS value
        WITH OFFSET AS ix
      )