INSERT INTO t (n1, n2, t1) VALUES (1, 2.34, 'abc');
INSERT INTO t VALUES (2, 1.56, 'ghi'), (3, 5.92, 'pqr');
INSERT INTO t VALUES (4, DEFAULT, 'xyz');
INSERT INTO t (i,k) SELECT * FROM u;
INSERT INTO t (i) SELECT max(j) FROM u;
INSERT INTO t DEFAULT VALUES;
INSERT INTO t (SELECT * FROM u);
INSERT INTO s.t(c1, c2, c3) VALUES((SELECT x FROM y), 'val1', 'val2');
INSERT INTO t (adate) values(current_timestamp)
