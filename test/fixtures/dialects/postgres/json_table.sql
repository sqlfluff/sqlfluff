-- PostgreSQL 17 JSON_TABLE syntax tests
-- Based on: https://www.postgresql.org/docs/17/functions-json.html#FUNCTIONS-SQLJSON-TABLE

-- FOR ORDINALITY and typed PATH columns, joined to the source table
SELECT
    o.order_id,
    li.line_no,
    li.sku,
    li.qty
FROM orders AS o,
    JSON_TABLE(
        o.doc,
        '$.line_items[*]'
        COLUMNS (
            line_no FOR ORDINALITY,
            sku text PATH '$.sku',
            qty integer PATH '$.qty'
        )
    ) AS li;

-- Lowercase function name, literal context item, implicit column path
SELECT jt.*
FROM json_table(
    '[{"a": 1, "b": "x"}]'::jsonb,
    '$[*]'
    COLUMNS (a int, b text)
) AS jt;

-- Named row path, ON EMPTY and ON ERROR behaviours on regular columns
SELECT jt.*
FROM products AS p,
    JSON_TABLE(
        p.doc,
        '$' AS root_path
        COLUMNS (
            product_name text PATH '$.name' DEFAULT 'unknown' ON EMPTY,
            price numeric PATH '$.price' DEFAULT 0 ON EMPTY NULL ON ERROR,
            stock integer PATH '$.stock' ERROR ON ERROR,
            tags jsonb PATH '$.tags' EMPTY ARRAY ON EMPTY,
            attrs jsonb PATH '$.attrs' EMPTY OBJECT ON ERROR
        )
    ) AS jt;

-- EXISTS columns, with and without PATH
SELECT jt.*
FROM products AS p,
    JSON_TABLE(
        p.doc,
        '$'
        COLUMNS (
            has_price boolean EXISTS PATH '$.price',
            has_tags boolean EXISTS PATH '$.tags' FALSE ON ERROR,
            is_active boolean EXISTS PATH '$.active' UNKNOWN ON ERROR,
            name boolean EXISTS
        )
    ) AS jt;

-- NESTED columns, with and without the PATH keyword, named and multi-level
SELECT jt.*
FROM shipments AS s,
    JSON_TABLE(
        s.doc,
        '$.packages[*]'
        COLUMNS (
            package_id text PATH '$.id',
            NESTED PATH '$.items[*]' AS items_path COLUMNS (
                item_no FOR ORDINALITY,
                item_sku text PATH '$.sku',
                NESTED '$.serials[*]' COLUMNS (
                    serial text PATH '$'
                )
            ),
            NESTED PATH '$.labels[*]' COLUMNS (label text PATH '$')
        )
    ) AS jt;

-- Table-level ON ERROR behaviours
SELECT jt.* FROM JSON_TABLE(
    '[1, 2]'::jsonb, '$[*]' COLUMNS (v int PATH '$') ERROR ON ERROR
) AS jt;

SELECT jt.* FROM JSON_TABLE(
    '[1, 2]'::jsonb, '$[*]' COLUMNS (v int PATH '$') EMPTY ON ERROR
) AS jt;

SELECT jt.* FROM JSON_TABLE(
    '[1, 2]'::jsonb, '$[*]' COLUMNS (v int PATH '$') EMPTY ARRAY ON ERROR
) AS jt;

-- Any behaviour in each ON ERROR position. PostgreSQL's grammar accepts these and
-- only rejects unsupported combinations when the query is analysed.
SELECT jt.* FROM JSON_TABLE(
    '[1]'::jsonb,
    '$[*]'
    COLUMNS (
        v int PATH '$' TRUE ON ERROR,
        e boolean EXISTS PATH '$' DEFAULT false ON ERROR
    )
    NULL ON ERROR
) AS jt;

-- LATERAL JSON_TABLE in an explicit join
SELECT
    o.order_id,
    li.sku
FROM orders AS o
CROSS JOIN LATERAL JSON_TABLE(
    o.doc,
    '$.line_items[*]'
    COLUMNS (sku text PATH '$.sku')
) AS li;
