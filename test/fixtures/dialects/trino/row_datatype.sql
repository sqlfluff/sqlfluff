SELECT
    name,
    CAST(ROW(price, store) AS ROW(price REAL, store VARCHAR)) AS data_row
FROM customers;

select CAST(ROW(1, 2.0) AS ROW(x BIGINT, y DOUBLE)).x;
