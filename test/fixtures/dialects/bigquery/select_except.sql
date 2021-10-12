SELECT
    * EXCEPT (seqnum) REPLACE (foo as bar, baz foobar)
FROM my_tbl;

-- Catch potential bugs in unions
select * except (foo) from some_table
union all
select * from another_table;

-- Except is allowed after other fields
select
  1 + 2 as calculated,
  * except (irrelevant)
from my_tbl;

-- This might be redundant with the example above.
-- Demonstrates using multiple except clauses.
select
  foo.* except (some_column),
  bar.* except (other_column)
from my_tbl;
