SELECT
  is_sensitive,
  breach_date,
  total_number_of_affected_accounts,
  SUM(total_number_of_affected_accounts) OVER (
    PARTITION BY is_sensitive
    ORDER BY is_sensitive, breach_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS cumulative_number_of_affected_accounts
FROM
  table1
