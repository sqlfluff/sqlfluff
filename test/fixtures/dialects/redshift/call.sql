CALL test_proc();

CALL test_proc(pg_last_query_id());

CALL outer_proc(5);

call test_sp1(3,'book');

call test_sp2(2,'2019');
