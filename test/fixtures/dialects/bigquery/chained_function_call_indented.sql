SELECT
    (foo)
        .LOWER()
        .TRIM() AS cleaned,
    (bar).UPPER().TRIM() AS other_value
FROM t;
