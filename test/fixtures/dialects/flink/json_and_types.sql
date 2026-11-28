CREATE TABLE inline_pk_and_types (
    id BIGINT PRIMARY KEY NOT ENFORCED,
    alt_id BIGINT CONSTRAINT pk_alt PRIMARY KEY NOT ENFORCED,
    event_ltz TIMESTAMP(3) WITH LOCAL TIME ZONE,
    event_ntz TIMESTAMP(3) WITHOUT TIME ZONE,
    clock_time TIME(3) WITHOUT TIME ZONE,
    details ROW<a INT 'field a', b STRING COMMENT 'field b'>,
    tags STRING ARRAY,
    required_ids INT NOT NULL ARRAY,
    bag STRING MULTISET
) WITH (
    'connector' = 'print'
);

CREATE TABLE derived_table LIKE inline_pk_and_types (
    INCLUDING ALL
    EXCLUDING DISTRIBUTION
    INCLUDING METADATA
);

SELECT
    MULTISET[1, 2, 3] AS nums,
    JSON_VALUE('{"a": 1}', '$.a' RETURNING INT DEFAULT 0 ON EMPTY ERROR ON ERROR) AS val,
    JSON_QUERY(
        '{"a": [1, 2]}',
        '$.a'
        RETURNING ARRAY<INT>
        WITH CONDITIONAL ARRAY WRAPPER
        EMPTY ARRAY ON EMPTY
        NULL ON ERROR
    ) AS arr,
    JSON_QUERY(
        doc,
        '$.items'
        WITHOUT ARRAY WRAPPER
        EMPTY OBJECT ON EMPTY
        ERROR ON ERROR
    ) AS obj,
    JSON_EXISTS('{"a": 1}', '$.a' FALSE ON ERROR) AS has_a,
    doc IS JSON AS is_any_json,
    doc IS JSON OBJECT AS is_obj,
    doc IS NOT JSON ARRAY AS not_arr,
    doc IS JSON SCALAR AS is_scalar,
    doc IS JSON VALUE AS is_val
FROM docs;
