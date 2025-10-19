MODEL (
  name model_with_macros,
  kind VIEW
);

SELECT 
    @each(
        ['id', 'name', 'email'],
        column -> column
    ),
    @if(@DEV, 'dev_flag', 'prod_flag') as environment_flag,
    created_at + INTERVAL 1 DAY as next_day
FROM simple_model
WHERE created_at >= @start_date
