-- `$` is an identifier character anywhere in a name.
CREATE TABLE t$x (c$1 INT, $c INT, d$ INT);
SELECT c$1, $c, d$ FROM t$x;
SELECT 1 AS a$b, 2 AS $a, 3 AS $, 4 AS $1, 5 AS a$$, 6 AS a$b$;
-- Digits followed by `$` are a name, but a decimal or an exponent ends first.
SELECT 1 AS 1$, 2 AS 12$3;
SELECT 1.5$x, 1e5$;
-- So are hexadecimal and bit values followed by a name character.
SELECT 1 AS 0x1F$, 2 AS 0x1Fg, 3 AS 0b1$, 4 AS 0b12, X'1F'$;
SET @a$b = 1;
-- MariaDB has no dollar-quoted strings, so these are names too.
SELECT 1 AS $$, 2 AS $a$, 3 AS $$a;
