MODEL (
  name simple_model,
  kind VIEW
);

SELECT 
    id,
    name,
    created_at
FROM source_table
