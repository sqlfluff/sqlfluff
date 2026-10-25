SELECT foo 'x' FROM t;

SELECT foo "x" FROM t;

SELECT DATE '2020-01-01', TIME '10:00', TIMESTAMP '2020-01-01 10:00';

SELECT _utf8mb4'x', _utf8mb4 'x', _latin1'x' COLLATE latin1_bin;

SELECT _binary'x', _utf8mb4 X'41', _utf8mb4 0x41, _latin1 b'1000001';

SELECT N'x', n'x', N'it''s';

SELECT N"x" FROM t;

SELECT _utf8mb4"x", _UTF8MB4'x';

SELECT _gb18030'x' FROM t;

SELECT _nosuchcs 'x' FROM t;

SELECT N 'x' FROM t;

SELECT BINARY 'a' = 'A';

SELECT BINARY col FROM t;

SELECT 1 FROM t WHERE a = BINARY 'x';
