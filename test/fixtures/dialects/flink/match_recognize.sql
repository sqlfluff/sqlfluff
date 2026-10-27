SELECT *
FROM Ticker
    MATCH_RECOGNIZE (
        PARTITION BY symbol
        ORDER BY rowtime
        MEASURES
            FIRST(A.price) AS start_price,
            LAST(A.price) AS top_price,
            B.price AS last_price
        ONE ROW PER MATCH
        AFTER MATCH SKIP TO LAST B
        PATTERN (A+ B)
        WITHIN INTERVAL '5' MINUTE
        DEFINE
            A AS LAST(A.price, 1) IS NULL OR A.price > LAST(A.price, 1),
            B AS B.price < LAST(A.price)
    ) AS matches;

SELECT *
FROM Ticker
    MATCH_RECOGNIZE (
        PARTITION BY symbol
        ORDER BY rowtime
        MEASURES
            A.price AS price
        ONE ROW PER MATCH
        AFTER MATCH SKIP PAST LAST ROW
        PATTERN (A{1,2} B* C? D+)
        DEFINE
            A AS TRUE,
            B AS TRUE,
            C AS TRUE,
            D AS TRUE
    ) matches
ORDER BY symbol;

SELECT *
FROM Ticker
    MATCH_RECOGNIZE (
        PARTITION BY symbol
        ORDER BY rowtime
        MEASURES
            A.price AS price
        ONE ROW PER MATCH
        PATTERN (A+ B | C+ D)
        DEFINE
            A AS TRUE,
            B AS TRUE,
            C AS TRUE,
            D AS TRUE
    ) matches;

SELECT *
FROM Ticker
    MATCH_RECOGNIZE (
        PARTITION BY symbol
        ORDER BY rowtime
        MEASURES
            A.price AS price
        ONE ROW PER MATCH
        PATTERN ((A B | C D) E)
        DEFINE
            A AS TRUE,
            B AS TRUE,
            C AS TRUE,
            D AS TRUE,
            E AS TRUE
    ) matches;
