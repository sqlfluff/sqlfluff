SELECT 
    id,
    name,
    email,
    created_at,
    'development' as env
FROM source_table  
WHERE created_at BETWEEN '2023-01-01' AND '2023-01-02'
