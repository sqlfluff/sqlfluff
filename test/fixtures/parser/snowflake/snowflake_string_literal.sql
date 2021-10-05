-- In snowflake, a double single quote resolves as a single quote in the string.
-- https://docs.snowflake.com/en/sql-reference/data-types-text.html#single-quoted-string-constants
SELECT '['']'
