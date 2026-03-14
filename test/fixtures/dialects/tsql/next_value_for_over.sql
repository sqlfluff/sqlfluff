-- NEXT VALUE FOR with OVER clause
-- https://learn.microsoft.com/en-us/sql/t-sql/functions/next-value-for-transact-sql

-- Basic OVER clause with ORDER BY
SELECT NEXT VALUE FOR my_sequence OVER (ORDER BY some_column) AS new_id
FROM my_table;

-- OVER clause with multiple ORDER BY columns
SELECT
    NEXT VALUE FOR dbo.seq1 OVER (ORDER BY col1, col2 DESC) AS seq_num,
    col1,
    col2
FROM my_table;

-- OVER clause with COLLATE
SELECT
    NEXT VALUE FOR schema1.my_seq OVER (ORDER BY name COLLATE Latin1_General_CI_AS) AS id
FROM users;

-- Multiple NEXT VALUE FOR with different sequences
SELECT
    NEXT VALUE FOR seq1 OVER (ORDER BY date_column) AS id1,
    NEXT VALUE FOR seq2 OVER (ORDER BY date_column) AS id2,
    data
FROM transactions;

-- NEXT VALUE FOR without OVER clause (still supported)
SELECT NEXT VALUE FOR my_sequence AS next_val;

-- NEXT VALUE FOR in INSERT statement with OVER
INSERT INTO target_table (id, data)
SELECT
    NEXT VALUE FOR my_seq OVER (ORDER BY source_id),
    data
FROM source_table;
