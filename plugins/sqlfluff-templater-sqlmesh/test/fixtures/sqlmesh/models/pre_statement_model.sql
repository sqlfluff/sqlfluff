MODEL (
  name pre_statement_model,
  kind FULL
);

@DEF(local_flag, TRUE);

SELECT
    id AS id,
    created_at
FROM source_table
WHERE created_at >= @start_ds
