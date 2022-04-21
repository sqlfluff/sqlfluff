INSERT OVERWRITE TABLE foo
PARTITION (a = 'test_foo', b) IF NOT EXISTS
SELECT a, 'test_bar' AS b FROM bar;

INSERT OVERWRITE TABLE foo
PARTITION (a, b) IF NOT EXISTS
SELECT 'test_foo' AS a, 'test_bar' AS b FROM bar;
