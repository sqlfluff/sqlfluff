INSERT INTO x FORMAT CSV;

INSERT INTO t (a, b) FORMAT CSV;

INSERT INTO t SETTINGS async_insert = 1 FORMAT JSONEachRow;

INSERT INTO t (a, b) SETTINGS async_insert = 1, wait_for_async_insert = 0 FORMAT CSV;

INSERT INTO t (a, b) SETTINGS async_insert = 1 VALUES (1, 'a');

INSERT INTO t SELECT a FROM b FORMAT TabSeparated;
