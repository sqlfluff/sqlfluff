/*
Examples from
https://www.ibm.com/docs/en/db2/11.5?topic=statements-call
*/
-- Call with positional parameters
CALL FOO(I1, I2);

-- Call with named argument
CALL Y.UPDATE_ORDER(TEST => 5);

-- Call with positional and named argument
CALL UPDATE_ORDER(5000, NEW_STATUS => 'Shipped');

-- Call with positional and multiple named arguments
CALL UPDATE_ORDER(
    5002,
    IN_CUSTID => 1001,
    NEW_STATUS => 'Received',
    NEW_COMMENTS => 'Customer satisfied with the order.'
);

/*
Examples from
https://www.ibm.com/docs/en/db2/11.5?topic=commands-runstats-using-admin-cmd
*/
CALL SYSPROC.ADMIN_CMD(
    'RUNSTATS ON TABLE employee ON KEY COLUMNS and INDEXES ALL'
);

/*
Test for no parameters.
*/
CALL DO_THE_THING();

/*
Test for no parenthesis.
*/
CALL DO_THE_THING;
