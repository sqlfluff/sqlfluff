-- Refer to a macro which doesn't exist
-- https://github.com/sqlfluff/sqlfluff/issues/3849
select * from {{ invalid_macro() }}
