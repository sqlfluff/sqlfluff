INSERT INTO test (id, col1) OVERRIDING SYSTEM VALUE VALUES (1, 'val');
INSERT INTO foo (bar) VALUES(current_timestamp);
INSERT INTO distributors AS d (did, dname) VALUES (8, 'Anvil Distribution');
