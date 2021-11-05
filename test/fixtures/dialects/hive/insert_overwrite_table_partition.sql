INSERT OVERWRITE TABLE foo
PARTITION (a='test_foo', b='test_bar') IF NOT EXISTS
SELECT a, b, c, d FROM bar;
