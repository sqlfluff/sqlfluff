SELECT 
    id,
    name,
    email,
    'dev_flag' as environment_flag,
    DATE_ADD('day', 1, created_at) as next_day
FROM model_with_macros
WHERE created_at >= '2023-01-01'
