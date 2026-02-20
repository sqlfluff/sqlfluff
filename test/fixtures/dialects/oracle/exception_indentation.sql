-- Test simple exception block
BEGIN
    SELECT 1 FROM dual;
    EXCEPTION
        WHEN no_data_found THEN
            DBMS_OUTPUT.PUT_LINE('No data');
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Error');
END;


-- Test nested exception blocks
DECLARE
    v_value NUMBER;
BEGIN
    BEGIN
        v_value := 1;
        EXCEPTION
            WHEN OTHERS THEN
                DBMS_OUTPUT.PUT_LINE('Inner exception');
    END;
    EXCEPTION
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Outer exception');
END;


-- Test exception with multiple handlers
BEGIN
    NULL;
    EXCEPTION
        WHEN zero_divide THEN
            DBMS_OUTPUT.PUT_LINE('Division by zero');
        WHEN invalid_number THEN
            DBMS_OUTPUT.PUT_LINE('Invalid number');
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Other error');
END;
