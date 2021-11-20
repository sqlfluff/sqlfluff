CALL MyStoredProcedure(CURRENT_ROLE());
CALL sv_proc1('Manitoba', 127.4);

SET Variable1 = 49;
CALL sv_proc2($Variable1);
