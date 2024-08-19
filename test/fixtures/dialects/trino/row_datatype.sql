SELECT
    name,
    CAST(ROW(price, store) AS ROW(price REAL, store VARCHAR)) AS data_row
FROM customers
