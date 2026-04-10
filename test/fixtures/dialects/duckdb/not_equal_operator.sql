-- Regression test for https://github.com/sqlfluff/sqlfluff/issues/7741
-- DuckDB allows postfix `!` as a factorial operator, which used to collide
-- with `!=` because the lexer emitted `!` and `=` as two separate tokens,
-- letting the factorial parser eagerly consume the `!`. Now `!=` is lexed
-- as a single `not_equal` token so the factorial path is never reached.

SELECT 1 WHERE a != b;

SELECT 1 WHERE a != 0 AND b != 'foo';

SELECT * FROM t WHERE col1 != col2;

-- The `<>` form must continue to work too.
SELECT 1 WHERE a <> b;

-- Factorial-then-equality should still parse: `(5!) = 120`.
SELECT 1 WHERE 5! = 120;

-- And the inverse: `5! != 119` — factorial then not-equal.
SELECT 1 WHERE 5! != 119;
