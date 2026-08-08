USING EXTERNAL FUNCTION simple(input VARCHAR)
    RETURNS VARCHAR
    LAMBDA 'some-name'
SELECT
    simple(bar)
FROM
    foo;

USING EXTERNAL FUNCTION first(input VARCHAR)
    RETURNS VARCHAR
    LAMBDA 'some-name',
EXTERNAL FUNCTION second(input VARCHAR)
    RETURNS VARCHAR
    LAMBDA 'some-name',
EXTERNAL FUNCTION third(input VARCHAR)
    RETURNS VARCHAR
    LAMBDA 'some-name'
SELECT
    first(bar),
    second(bar),
    third(bar)
FROM
    foo;

USING EXTERNAL FUNCTION complex_types(input ARRAY(VARCHAR))
    RETURNS ARRAY(VARCHAR)
    LAMBDA 'some-name'
SELECT
    complex_types(ARRAY['foo'])
FROM
    foo;

USING EXTERNAL FUNCTION no_args()
    RETURNS INTEGER
    LAMBDA 'some-name'
SELECT
    no_args();

USING EXTERNAL FUNCTION multi_args(first_input VARCHAR, second_input INTEGER)
    RETURNS VARCHAR
    LAMBDA 'some-name'
SELECT
    multi_args(bar, 1)
FROM
    foo;
