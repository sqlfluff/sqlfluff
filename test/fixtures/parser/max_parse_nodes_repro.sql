-- A synthesized reproduction of the `max_parse_nodes` accounting bug.
--
-- The Python parser used to charge inserted segments only for zero-length
-- matches, while the Rust parser charged them unconditionally. On a file like
-- this one that meant the Rust engine hit the node limit while Python sailed
-- under it (originally on the 1448-line Spark `decimalPrecision.sql`, which
-- measured ~96k nodes in Python and ~108k in Rust). The engines must agree on
-- the node budget; see `test/core/parser/max_parse_nodes_test.py`.
--
-- The wide CAST expressions are deliberate: each bracketed type produces
-- inserted (implicit) segments, which is what the two engines used to count
-- differently.
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
SELECT cast(1 as tinyint) + cast(1 as decimal(3, 0)) FROM t;
