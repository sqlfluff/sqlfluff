SELECT * FROM t MATCH_RECOGNIZE (ORDER BY a PATTERN (x+) DEFINE x AS a > 1);

SELECT
    *
FROM orders MATCH_RECOGNIZE (
    PARTITION BY custkey
    ORDER BY orderdate
    MEASURES
        A.totalprice AS starting_price,
        LAST(B.totalprice) AS bottom_price,
        LAST(U.totalprice) AS top_price
    ONE ROW PER MATCH
    AFTER MATCH SKIP PAST LAST ROW
    PATTERN (A B+ C+ D+)
    SUBSET U = (C, D)
    DEFINE
        B AS totalprice < PREV(totalprice),
        C AS totalprice > PREV(totalprice) AND totalprice <= A.totalprice,
        D AS totalprice > PREV(totalprice)
);

SELECT
    *
FROM orders MATCH_RECOGNIZE (
    ORDER BY orderdate
    MEASURES A.totalprice AS starting_price
    ALL ROWS PER MATCH
    PATTERN (A {- B+ C+ -} D+)
    DEFINE
        B AS totalprice < PREV(totalprice),
        C AS totalprice > PREV(totalprice),
        D AS totalprice > PREV(totalprice)
);

SELECT * FROM t MATCH_RECOGNIZE (ORDER BY a PATTERN (PERMUTE(A, B, C)) DEFINE A AS true);

SELECT * FROM t MATCH_RECOGNIZE (ORDER BY a PATTERN (^A{2,4}?B*$) DEFINE A AS true);

SELECT * FROM t MATCH_RECOGNIZE (ORDER BY a MEASURES A.totalprice AS p ALL ROWS PER MATCH SHOW EMPTY MATCHES PATTERN (A*) DEFINE A AS true);

SELECT * FROM t MATCH_RECOGNIZE (ORDER BY a MEASURES A.totalprice AS p ALL ROWS PER MATCH OMIT EMPTY MATCHES PATTERN (A*) DEFINE A AS true);

SELECT * FROM t MATCH_RECOGNIZE (ORDER BY a MEASURES A.totalprice AS p ALL ROWS PER MATCH WITH UNMATCHED ROWS PATTERN (A*) DEFINE A AS true);

SELECT * FROM t MATCH_RECOGNIZE (ORDER BY a AFTER MATCH SKIP TO NEXT ROW PATTERN (A+) DEFINE A AS true);

SELECT * FROM t MATCH_RECOGNIZE (ORDER BY a AFTER MATCH SKIP TO FIRST A PATTERN (A+ B+) DEFINE A AS true, B AS true);

SELECT * FROM t MATCH_RECOGNIZE (ORDER BY a AFTER MATCH SKIP TO LAST B PATTERN (A+ B+) DEFINE A AS true, B AS true);

SELECT
    *
FROM orders MATCH_RECOGNIZE (
    ORDER BY orderdate
    MEASURES A.totalprice AS starting_price
    PATTERN (START DOWN+ UP+ | DOWN+ UP+ END)
    DEFINE
        DOWN AS totalprice < PREV(totalprice),
        UP AS totalprice > PREV(totalprice)
);
