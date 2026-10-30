EXECUTE STATEMENT SET
BEGIN
    INSERT INTO orders SELECT * FROM orders_source;
    INSERT INTO customers SELECT * FROM customers_source;
END;

BEGIN STATEMENT SET;
INSERT INTO orders SELECT * FROM orders_source;
END;
