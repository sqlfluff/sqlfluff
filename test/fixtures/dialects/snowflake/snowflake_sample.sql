-- https://github.com/sqlfluff/sqlfluff/issues/547
select *
-- 20% sample
from real_data sample (20)
;

SET sample_size = 10;
WITH dummy_data AS (
    SELECT SEQ4() AS row_number
    FROM TABLE(GENERATOR(rowcount => 1000))
    ORDER BY row_number
)
SELECT * FROM dummy_data SAMPLE ($sample_size ROWS);
