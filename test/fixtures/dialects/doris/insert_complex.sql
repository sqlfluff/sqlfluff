INSERT INTO test PARTITION(p1, p2) WITH LABEL label1 (c1, c2) SELECT id, name FROM test2;
