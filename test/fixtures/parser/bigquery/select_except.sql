SELECT
    * EXCEPT (seqnum) REPLACE (foo as bar, baz foobar)
FROM my_tbl;

-- Catch potential bugs in unions
select * except (foo) from some_table
union all
select * from another_table
