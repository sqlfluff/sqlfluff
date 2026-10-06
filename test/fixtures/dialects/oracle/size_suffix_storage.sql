-- Oracle size units are K/M/G/T/P/E (case-insensitive).
-- The numeric lexer must accept the digit run when a size suffix follows.
CREATE TABLE t (c NUMBER)
STORAGE (
    INITIAL 10P
    NEXT 10E
    MINEXTENTS 1
);
