CALL MyStoredProcedure(CURRENT_ROLE());
CALL sv_proc1('Manitoba', 127.4);

SET Variable1 = 49;
CALL sv_proc2($Variable1);

CALL sv_proc1('Manitoba', 127.4) INTO :ret1;
CALL sv_proc1('Manitoba', 127.4) INTO ret1;
CALL my_db.my_schema.sv_proc1() INTO :result;
CALL my_db.my_schema.sv_proc1() INTO result;
CALL sv_proc1(a => 1, b => 'x') INTO :ret1;
CALL sv_proc1(a => 1, b => 'x') INTO ret1;

DECLARE
    myvar VARCHAR DEFAULT NULL;
BEGIN
    CALL myproc('arg') INTO :myvar;
    CALL myproc('arg') INTO myvar;
    RETURN :myvar;
END;
