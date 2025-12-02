-- In snowflake, a double single quote resolves as a single quote in the string.
-- https://docs.snowflake.com/en/sql-reference/data-types-text.html#single-quoted-string-constants
SELECT '['']';

-- Snowflake allows dollar quoted string literals
select $$abc$$;
