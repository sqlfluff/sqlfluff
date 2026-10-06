-- MariaDB sequence value expressions.
-- NEXT VALUE FOR seq     == NEXTVAL(seq)
-- PREVIOUS VALUE FOR seq == LASTVAL(seq)
-- https://mariadb.com/kb/en/sequence-overview/

SELECT NEXT VALUE FOR s;

SELECT PREVIOUS VALUE FOR s;

-- Schema-qualified sequence name.
SELECT NEXT VALUE FOR my_schema.s;

-- Usable wherever an expression is valid.
INSERT INTO t (id) VALUES (NEXT VALUE FOR s);

-- As a column DEFAULT, bracketed and bare (both accepted by MariaDB).
CREATE TABLE t_bracketed (a INT PRIMARY KEY DEFAULT (NEXT VALUE FOR s), b INT);

CREATE TABLE t_bare (a INT DEFAULT NEXT VALUE FOR s);
