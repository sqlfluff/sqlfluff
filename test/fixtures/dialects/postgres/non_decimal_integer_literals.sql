-- Non-decimal integer literals (Postgres 16)
-- https://www.postgresql.org/docs/16/sql-syntax-lexical.html#SQL-SYNTAX-CONSTANTS-NUMERIC
SELECT 0x1F, 0o17, 0b101;

SELECT 0X1f, 0O17, 0B101;

-- Underscores between digits, and after the prefix
SELECT 0xFFFF_FFFF, 0o_1_755, 0b10001000_00000000, 0x_FF, 1_000_000;

SELECT -0x42, 0b101::int, 0xFF + 0o7 AS total;

SELECT * FROM t WHERE flags & 0b100 = 0b100 AND id > 0x10;

-- Decimal forms are unchanged
SELECT 0, 1e10, .5, 12., 1::int, 1.618_034;
