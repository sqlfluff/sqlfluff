EXCEPTION
  WHEN EXCEPTION_2 THEN
    RETURN SQLERRM;
  WHEN EXCEPTION_1 THEN
    RETURN SQLERRM;

EXCEPTION
  WHEN MY_FIRST_EXCEPTION OR MY_SECOND_EXCEPTION THEN
    RETURN 123;
  WHEN MY_FOURTH_EXCEPTION THEN
    RETURN 4;
  WHEN OTHER THEN
    RETURN 99;

EXCEPTION
  WHEN STATEMENT_ERROR THEN
    RETURN OBJECT_CONSTRUCT('Error type', 'STATEMENT_ERROR',
                            'SQLCODE', SQLCODE,
                            'SQLERRM', SQLERRM,
                            'SQLSTATE', SQLSTATE);
  WHEN EXPRESSION_ERROR THEN
    RETURN OBJECT_CONSTRUCT('Error type', 'EXPRESSION_ERROR',
                            'SQLCODE', SQLCODE,
                            'SQLERRM', SQLERRM,
                            'SQLSTATE', SQLSTATE);
  WHEN OTHER THEN
    RETURN OBJECT_CONSTRUCT('Error type', 'Other error',
                            'SQLCODE', SQLCODE,
                            'SQLERRM', SQLERRM,
                            'SQLSTATE', SQLSTATE);

EXCEPTION
        WHEN STATEMENT_ERROR THEN
            RETURN OBJECT_CONSTRUCT('Error type', 'STATEMENT_ERROR',
                                    'SQLCODE', SQLCODE,
                                    'SQLERRM', SQLERRM,
                                    'SQLSTATE', SQLSTATE);
        WHEN EXPRESSION_ERROR THEN
            RETURN OBJECT_CONSTRUCT('Error type', 'EXPRESSION_ERROR',
                                    'SQLCODE', SQLCODE,
                                    'SQLERRM', SQLERRM,
                                    'SQLSTATE', SQLSTATE);
        WHEN OTHER THEN
            RETURN OBJECT_CONSTRUCT('Error type', 'Other error',
                                    'SQLCODE', SQLCODE,
                                    'SQLERRM', SQLERRM,
                                    'SQLSTATE', SQLSTATE);

EXCEPTION
    WHEN OTHER THEN
        ROLLBACK;
        RAISE;

EXCEPTION
    WHEN MY_EXCEPTION THEN
        LET err_msg := SQLERRM;
        RETURN err_msg;
    WHEN OTHER THEN
        ROLLBACK;
        RAISE;

BEGIN
    LET x NUMBER := 1;
EXCEPTION
    WHEN OTHER THEN
        RETURN 'handled';
END;

BEGIN
    LET x NUMBER := 1;
EXCEPTION
    WHEN MY_EXCEPTION OR MY_OTHER_EXCEPTION THEN
        LET err_msg := SQLERRM;
        RETURN err_msg;
    WHEN OTHER THEN
        ROLLBACK;
        RAISE;
END;

BEGIN
    IF (TRUE) THEN
        BEGIN
            LET x NUMBER := 1;
        EXCEPTION
            WHEN OTHER THEN
                RETURN 'inner';
        END;
    END IF;

    RETURN 'ok';
EXCEPTION
    WHEN OTHER THEN
        RETURN 'outer';
END;

BEGIN
    LET x NUMBER := 1;
EXCEPTION
    WHEN OTHER THEN
        BEGIN
            RETURN 'nested block in handler';
        END;
END;
