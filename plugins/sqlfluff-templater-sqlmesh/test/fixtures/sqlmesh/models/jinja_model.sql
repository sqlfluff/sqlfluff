MODEL (
  name jinja_model,
  kind FULL
);

JINJA_QUERY_BEGIN;
SELECT
  id AS id,
  {{ 'dev' if is_dev else 'prod' }} AS env
FROM source_table;
JINJA_END;
