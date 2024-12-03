INSERT INTO TABLE db.foo SELECT col1, col2 FROM db.foo2;

INSERT INTO TABLE db.foo VALUES ((1, 'a'), (2, 'b'));

INSERT INTO TABLE db.foo PARTITION (col1, col2) SELECT col1, col2, col3 FROM db.foo2;

INSERT INTO TABLE db.foo PARTITION (col1=1, col2='a') SELECT col3 FROM db.foo2;

INSERT INTO TABLE db.foo [SHUFFLE] SELECT col1, col2 FROM db.foo2;

INSERT INTO TABLE db.foo [NOSHUFFLE] SELECT col1, col2 FROM db.foo2;

INSERT INTO db.foo (col1, col2) SELECT col1, col2 FROM db.foo2 WHERE col2 > 100;
