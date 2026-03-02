-- Basic JSON_TABLE with FOR ORDINALITY column
SELECT
    jt.seq,
    jt.letter
FROM json_table(
    '["A","B","C"]',
    '$[*]'
    COLUMNS (
        seq FOR ORDINALITY,
        letter VARCHAR2(10) PATH '$'
    )
) AS jt;

-- JSON_TABLE with only a regular column
SELECT
    jt.val
FROM json_table(
    '{"name": "test"}',
    '$'
    COLUMNS (
        val VARCHAR2(100) PATH '$.name'
    )
) jt;

-- JSON_TABLE with multiple columns including FOR ORDINALITY and type with error handling
SELECT
    jt.rn,
    jt.name
FROM json_table(
    '[{"name":"Alice"},{"name":"Bob"}]',
    '$[*]'
    COLUMNS (
        rn FOR ORDINALITY,
        name VARCHAR2(50) PATH '$.name' NULL ON ERROR
    )
) jt;
