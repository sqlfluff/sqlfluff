-- A token whose raw contains a non-word character is a code boundary:
-- a following keyword starts the next clause even without whitespace
-- between them. Only a fully word-like token could have absorbed the
-- keyword in the lexer.
SELECT *FROM t;

SELECT a.*FROM t;

SELECT a, *FROM t;

SELECT 'x'FROM t;

SELECT "col"FROM t;

SELECT a /* c */FROM t;
