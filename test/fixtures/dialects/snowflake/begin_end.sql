-- NOTE: This is a loop BEGIN, and not a transaction BEGIN,
-- because BEGIN is  NOT followed immediately by a ";"
-- See: https://docs.snowflake.com/en/sql-reference/sql/begin
-- See: https://docs.snowflake.com/en/sql-reference/snowflake-scripting/begin
begin
select 1;
select 2;
begin
select 3;
select 4;
end;
end;
