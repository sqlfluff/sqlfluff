SELECT
  CONVERT(nvarchar(100), first_column) as first,
  TRY_CONVERT(float, second_column) as second
FROM some_table;

SELECT
  CONVERT(varchar(32), getdate(), 101) fixed_style,
  CONVERT(varchar(32), getdate(), @style) var_style,
  CONVERT(varchar(32), getdate(), IIF(@config=1, 101, 1)) exp_style;
