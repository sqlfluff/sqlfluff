SELECT
  CONVERT(nvarchar(100), first_column) as first,
  TRY_CONVERT(float, second_column) as second
FROM some_table
