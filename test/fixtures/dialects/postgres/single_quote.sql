SELECT '';

SELECT '''';

SELECT '

';

SELECT '''aaa''';

SELECT '
''
';

SELECT '\';

SELECT 'foo'
'bar';

SELECT 'foo'


'bar';

SELECT 'foo'


     'bar';

SELECT 'foo' -- some comment
'bar';

COMMENT ON TABLE "some_table" IS E''
'This is a valid comment style'
'\n\n'
'which is escaped';

SELECT U&''
'This is a valid comment style '
'd\0061t\+000061'
' which has unicode';

SELECT b''
'000'
'010'
'101';

SELECT x'1234'
'abcd'
'dead'
'beef';
