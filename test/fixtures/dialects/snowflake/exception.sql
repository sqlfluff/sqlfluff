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
