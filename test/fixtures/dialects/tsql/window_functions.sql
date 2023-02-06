-- Classical partition/order by
SELECT ROW_NUMBER() OVER(PARTITION BY t.col1 ORDER BY t.col2) rn
FROM mytable t;

-- Partition by constant
SELECT ROW_NUMBER() OVER(PARTITION BY 1 ORDER BY t.col2) rn
FROM mytable t;

-- Partition by expression
SELECT ROW_NUMBER() OVER(PARTITION BY CASE WHEN t.col1 = 'value' THEN 1 END ORDER BY t.col2) rn
FROM mytable t;

-- Partition by expression and column
SELECT ROW_NUMBER() OVER(PARTITION BY t.col3, CASE WHEN t.col1 = 'value' THEN 1 END, t.col4 ORDER BY t.col2) rn
FROM mytable t;

-- Partition by select statement
SELECT ROW_NUMBER() OVER(PARTITION BY (SELECT col1 FROM othertable) ORDER BY t.col2) rn
FROM mytable t;

-- Partition by aggregate
SELECT ROW_NUMBER() OVER(PARTITION BY SUM(t.col1) ORDER BY t.col2) rn
FROM mytable t
GROUP BY t.col2;
