set v1 = 10;

set v2 = 'example';

set (v1, v2) = (10, 'example');

set id_threshold = (select count(*) from table1) / 2;

set (min, max) = (40, 70);

set (min, max) = (50, 2 * $min);

SET THIS_ROLE=CURRENT_ROLE();

SET (rec_updated_cutoff_orders, rec_updated_cutoff_deliverables) = (
    SELECT
        COALESCE(MAX(CASE WHEN entity_type = 'x' THEN rec_updated_at::DATE END), '2013-01-01')
        , COALESCE(MAX(CASE WHEN entity_type = 'x' THEN rec_updated_at::DATE END), '2025-01-01')
    FROM test.x
);
