MODEL (
  name python_macro_model,
  kind FULL
);

SELECT
    id AS id,
    @to_upper(name) AS upper_name
FROM source_table
