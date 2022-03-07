INSERT INTO foo (bar) VALUES(current_timestamp);

INSERT INTO foo (bar, baz) VALUES(1, 2), (3, 4);

INSERT INTO foo (bar, baz) VALUES(1 + 1, 2), (3, 4);

INSERT INTO foo (bar) VALUES(DEFAULT);

INSERT INTO distributors AS d (did, dname) VALUES (8, 'Anvil Distribution');

INSERT INTO test (id, col1) OVERRIDING SYSTEM VALUE VALUES (1, 'val');

INSERT INTO test (id, col1) OVERRIDING USER VALUE VALUES (1, 'val');

INSERT INTO foo (bar) DEFAULT VALUES;

INSERT INTO films SELECT * FROM tmp_films WHERE date_prod < '2004-05-07';

INSERT INTO foo (bar) VALUES(current_timestamp)
RETURNING *;

INSERT INTO foo (bar) VALUES(current_timestamp)
RETURNING bar;

INSERT INTO foo (bar) VALUES(current_timestamp)
RETURNING bar AS some_alias;

INSERT INTO foo (bar, baz) VALUES(1, 2)
RETURNING bar, baz;

INSERT INTO foo (bar, baz) VALUES(1, 2)
RETURNING bar AS alias1, baz AS alias2;
