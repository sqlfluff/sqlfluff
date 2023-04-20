SELECT 1 + (2 * 3) >= 4 + 6+13 as val;

SELECT 1 + ~(~2 * 3) >= 4 + ~6+13 as val;

SELECT -1;

SELECT -1 + 5;

SELECT ~1;

SELECT -1 + ~5;

SELECT 4 & ~8 | 16;

SELECT 8 + ~(3);

SELECT 8 | ~ ~ ~4;

SELECT 1 * -(5);

SELECT 1 * -5;

SELECT 1 * - - - 5;

SELECT 1 * - - - (5);

SELECT 1 * + + (5);

SELECT 1 * - - - func(5);

SELECT 1 * ~ ~ ~ func(5);

SELECT 1 * +(5);

SELECT 1 * +5;

SELECT 1 * + + 5;

SELECT FALSE AND NOT (TRUE);

SELECT FALSE AND NOT NOT NOT (TRUE); -- parses middle NOT as column ref

SELECT FALSE AND NOT (TRUE);

SELECT FALSE AND NOT func(5);

SELECT 'abc' LIKE - - 5; -- PG can parse this ok, and then fail due to data type mismatch

SELECT 'abc' LIKE ~ ~ 5; -- PG can parse this ok, and then fail due to data type mismatch
