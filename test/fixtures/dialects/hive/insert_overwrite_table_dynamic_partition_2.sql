INSERT OVERWRITE TABLE foo
PARTITION (a, b) IF NOT EXISTS
SELECT 'test_foo' AS a, 'test_bar' AS b FROM bar;
