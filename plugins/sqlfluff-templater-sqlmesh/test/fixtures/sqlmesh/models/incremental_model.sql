MODEL (
  name incremental_model,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column created_at
  ),
  start '2023-01-01',
  cron '@daily'
);

SELECT 
    id,
    name,
    email,
    created_at,
    @if(@is_dev, 'development', 'production') as env
FROM source_table  
WHERE created_at BETWEEN @start_ds AND @end_ds
