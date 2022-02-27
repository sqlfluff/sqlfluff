-- TVFs that can be specified in SELECT/LATERAL VIEW clauses

-- explode in a SELECT
SELECT explode(array(10, 20));

-- explode_outer in a SELECT
SELECT explode_outer(array(10, 20));

-- explode in a LATERAL VIEW clause
SELECT
    test.a,
    test.b
FROM test
    LATERAL VIEW explode(array(3, 4)) AS c2;

-- explode_outer in a LATERAL VIEW clause
SELECT
    test.a,
    test.b
FROM test
    LATERAL VIEW explode_outer(array(3, 4)) AS c2;

-- inline in a SELECT
SELECT inline(array(struct(1, 'a'), struct(2, 'b')));

-- inline_outer in a SELECT
SELECT inline_outer(array(struct(1, 'a'), struct(2, 'b')));

-- inline in a LATERAL VIEW clause
SELECT
    test.a,
    test.b
FROM test
    LATERAL VIEW inline(array(struct(1, 'a'), struct(2, 'b'))) AS c1, c2;

-- inline_outer in a LATERAL VIEW clause
SELECT
    test.a,
    test.b
FROM test
    LATERAL VIEW inline_outer(array(struct(1, 'a'), struct(2, 'b'))) AS c1, c2;

-- posexplode in a SELECT
SELECT posexplode(array(10, 20));

-- posexplode_outer in a SELECT
SELECT posexplode_outer(array(10, 20));

-- posexplode in a LATERAL VIEW clause
SELECT
    test.a,
    test.b
FROM test
    LATERAL VIEW posexplode(array(10, 20)) AS c1;

-- posexplode_outer in a LATERAL VIEW clause
SELECT
    test.a,
    test.b
FROM test
    LATERAL VIEW posexplode_outer(array(10, 20)) AS c1;

-- stack in a SELECT
SELECT stack(2, 1, 2, 3);

-- stack in a LATERAL VIEW clause
SELECT
    test.a,
    test.b
FROM test
    LATERAL VIEW stack(2, 1, 2, 3) AS c1, c2;

-- json_tuple in a SELECT
SELECT json_tuple('{"a":1, "b":2}', 'a', 'b');

-- json_tuple in a LATERAL VIEW clause
SELECT
    test.a,
    test.b
FROM test
    LATERAL VIEW json_tuple('{"a":1, "b":2}', 'a', 'b') AS c1, c2;

-- parse_url in a SELECT
SELECT parse_url('http://spark.apache.org/path?query=1', 'HOST');

-- parse_url in a LATERAL VIEW clause
SELECT
    test.a,
    test.b
FROM test
    LATERAL VIEW parse_url(
        'http://spark.apache.org/path?query=1', 'HOST'
    ) AS c1;
