-- https://github.com/sqlfluff/sqlfluff/issues/547
select *
-- 20% sample
from real_data sample (20)