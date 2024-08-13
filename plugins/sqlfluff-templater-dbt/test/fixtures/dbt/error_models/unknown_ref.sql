-- Refer to a relation which doesn't exist
-- https://github.com/sqlfluff/sqlfluff/issues/3849
select * from {{ ref("i_do_not_exist") }}
