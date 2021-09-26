CREATE OR REPLACE FUNCTION percentage ( fraction DECIMAL,
                                        entirety DECIMAL)
RETURN VARCHAR(10)
IS
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
END hello; /

