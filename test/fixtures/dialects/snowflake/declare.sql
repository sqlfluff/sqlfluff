DECLARE
    profit number(38, 2) DEFAULT 0.0;
    revenue number(38, 2) DEFAULT 110.0;
    c1 CURSOR FOR SELECT price FROM invoices;
    myexception EXCEPTION (-20000, 'my first exception');
BEGIN
    profit := 1.0;
END;

DECLARE
    res RESULTSET DEFAULT (SELECT price FROM invoices);
    c1 CURSOR FOR res;
BEGIN
    RETURN c1;
END;
