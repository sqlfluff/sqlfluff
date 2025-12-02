-- Plain BULK insert
BULK INSERT my_schema.my_table
FROM 'data.csv';

-- BULK insert with options
BULK INSERT my_schema.my_table
FROM 'data.csv'
WITH (
    BATCHSIZE = 1024,
    CHECK_CONSTRAINTS,
    ORDER (col1 ASC, col2 DESC),
    FORMAT = 'CSV'
);
