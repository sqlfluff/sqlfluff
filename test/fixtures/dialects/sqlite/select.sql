SELECT a FROM foo LIMIT 10;

SELECT
    survey_time
    , AVG(light) AS trips
FROM
    survey
GROUP BY survey_time;

WITH time_cte AS (
  SELECT
      branch,
      created_at,
      time,
      cast(time - LAG (time, 1, time) OVER (ORDER BY time) as real) AS time_spent
  FROM heartbeats h
  WHERE user_id = 1 AND created_at >= DATE('now', 'start of day')
  ORDER BY id
  LIMIT 1 OFFSET 1
)
SELECT
    branch as name,
    cast(time_spent as real) as time_spent,
    cast(time_spent / (SELECT SUM(time_spent) FROM time_cte) as real) as time_percentage
FROM (
    SELECT
        branch,
        cast(SUM(time_spent) as real) AS time_spent
    FROM time_cte
    GROUP BY branch
    ORDER BY time_spent DESC
)
;
