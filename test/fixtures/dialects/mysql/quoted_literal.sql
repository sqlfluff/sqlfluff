SELECT '';

SELECT '''';

SELECT '

';

SELECT '''aaa''';

SELECT '
''
';

SELECT 'foo'
'bar';

SELECT 'foo'   'bar';

SELECT 'foo'


'bar';

SELECT 'foo' -- some comment
'bar';

SELECT 'foo' /*  some comment */ 'bar';

UPDATE table1 SET column1 = 'baz\'s';

SELECT 'terminating MySQL-y escaped single-quote bazs\'';

SELECT 'terminating ANSI-ish escaped single-quote ''';

SELECT '\\';
