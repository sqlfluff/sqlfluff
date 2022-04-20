INSERT OVERWRITE TABLE foo
PARTITION (a = 'test_foo', b) IF NOT EXISTS
SELECT a, 'test_bar' AS b FROM bar;
