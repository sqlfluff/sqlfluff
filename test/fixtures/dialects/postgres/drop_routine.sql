DROP ROUTINE foo(integer);

DROP ROUTINE IF EXISTS s2.foobar(int), pr(int) CASCADE;

DROP ROUTINE IF EXISTS no_such_routine RESTRICT;
