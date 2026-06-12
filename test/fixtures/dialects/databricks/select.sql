select *
from shopify_cz.order
;

SELECT *
FROM IDENTIFIER('table_name')
;

SELECT *
FROM IDENTIFIER('schema_name' || '.table_name')
;

CREATE OR REFRESH MATERIALIZED VIEW my_view AS
SELECT
    id COLLATE UTF8_LCASE
FROM my_source;
