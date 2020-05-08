SELECT
    * EXCEPT (seqnum) REPLACE (foo as bar, baz foobar)
FROM my_tbl