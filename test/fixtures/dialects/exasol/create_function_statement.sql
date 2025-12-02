CREATE OR REPLACE FUNCTION percentage ( fraction DECIMAL,
                                        entirety DECIMAL)
RETURN VARCHAR(10)
AS
    res DECIMAL;
BEGIN
    res := (100*fraction)/entirety;
    RETURN res || ' %';
END percentage;
/
----
CREATE FUNCTION hello () RETURN VARCHAR(10)
AS
    res DECIMAL;
BEGIN
    res := hello.world("no");
    RETURN 'HELLO';
END hello;
/
----
CREATE FUNCTION case_function () RETURN VARCHAR(10)
AS
    res DECIMAL;
BEGIN
    res := CASE WHEN input_variable < 0 THEN 0 ELSE input_variable END;
    RETURN res;
END case_function;
/
----
CREATE FUNCTION assignment_function () RETURN VARCHAR(10)
AS
    res DECIMAL;
BEGIN
    res := 'Hello World';
    RETURN res;
END assignment_function;
/
----
CREATE FUNCTION if_function () RETURN VARCHAR(10)
AS
    res DECIMAL;
BEGIN
    IF input_variable = 0 THEN
        res := NULL;
    ELSEIF input_variable = 1 THEN
        res := 'HELLO';
    ELSEIF input_variable = 2 THEN
        res := 'HALLO';
    ELSE
        res := input_variable;
    END IF;
    RETURN res;
END if_function;
/
----
CREATE FUNCTION for_loop_function () RETURN VARCHAR(10)
AS
    res DECIMAL;
BEGIN
    FOR cnt := 1 TO input_variable
    DO
        res := res*2;
    END FOR;
    RETURN res;
END for_loop_function;
/
----
CREATE FUNCTION for_loop_function2 () RETURN VARCHAR(10)
AS
    res DECIMAL;
BEGIN
    FOR cnt IN 1..10 LOOP
        res := res*2;
    END LOOP;
    RETURN res;
END for_loop_function2;
/
----
CREATE FUNCTION for_loop_function3 () RETURN VARCHAR(10)
AS
    res DECIMAL;
BEGIN
    WHILE cnt <= input_variable
    DO
        res := res*2;
        cnt := cnt+1;
    END WHILE;
    RETURN res;
END for_loop_function3;
/
CREATE FUNCTION schem.func (
    p1 VARCHAR(6),
    p2 VARCHAR(10)
) RETURN VARCHAR (20)
IS
    res VARCHAR(20);

BEGIN

    IF p1 IS NOT NULL AND p2 IS NOT NULL THEN
        IF p1 = 1 THEN
            res:= 'Hello World';
        ELSE
            IF p2 = 3 THEN
                res:= 'ABC';
            END IF;
            res:= 'WOHOOOO';
        END IF;
    END IF;
    RETURN res;
END schem.func;
/
