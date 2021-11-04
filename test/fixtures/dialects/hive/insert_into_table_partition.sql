INSERT INTO TABLE foo
PARTITION (a='test_foo', b='test_bar')
SELECT a, b, c, d FROM bar;
