DECLARE
    profit number(38, 2) DEFAULT 0.0;
    revenue number(38, 2) DEFAULT 110.0;
    c1 CURSOR FOR SELECT price FROM invoices;
BEGIN
    profit := 1.0;
END;

-- DECLARE
--     res RESULTSET DEFAULT (SELECT price FROM invoices);
--     c1 CURSOR FOR res;