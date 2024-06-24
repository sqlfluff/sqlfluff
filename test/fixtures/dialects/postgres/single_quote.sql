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

SELECT
e'da' --this is a comment
'ta';

SELECT
e'value of newline here:
'
    'space '
'no'
'space';

SELECT U&''
'd\0061t\+000061'
' which has unicode',
U&'d!0061t!+000061'
' which has unicode' UESCAPE '!',
u&'d!0061t!+000061 which has unicode' uescape '!';

SELECT b''
'000'
'010'
'101';

SELECT x'1234'
'abcd'
'dead'
'beEF';

SELECT e'two '
'line',
E'can have single quotes escaped this way: \' ',
e'but the second line'
'requires it like this '' \n\n';
