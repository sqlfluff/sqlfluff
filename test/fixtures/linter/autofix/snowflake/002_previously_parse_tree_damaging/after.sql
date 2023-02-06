MERGE INTO foo.bar AS tgt
USING (
  SELECT foo::DATE AS bar
  FROM foo.bar
  WHERE
    split(foo, '|')[2] REGEXP '^\\d+\\-\\d+\\-\\d+ \\d+\\:\\d+$'
    OR foo IN ('BAR', 'FOO')
) AS src
  ON
    src.foo = tgt.foo
WHEN MATCHED THEN
  UPDATE SET
    tgt.foo = src.foo;
