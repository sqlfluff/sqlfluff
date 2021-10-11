SELECT
  *
FROM
  table_a
WHERE
  -- Tests that '<' is parsed correctly. (Since some dialects use angle
  -- brackets, e.g. ARRAY<INT64>, it's possible for a "<" in isolation to
  -- be parsed as an open angle bracket without a matching close bracket.
  a < b
