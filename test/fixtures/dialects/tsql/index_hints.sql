-- Test various INDEX hint syntaxes
-- https://learn.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-table

-- INDEX with list in brackets
SELECT * FROM dbo.table1 WITH (INDEX(ix_table_id));

-- Multiple indices in brackets
SELECT * FROM dbo.table1 WITH (INDEX(ix_table_id, ix_table_name));

-- INDEX with equals and brackets (currently supported)
SELECT * FROM dbo.table2 WITH (INDEX = (ix_table_id));

-- INDEX with equals without brackets (needs support)
SELECT * FROM dbo.table3 WITH (INDEX = ix_table_id);

-- INDEX with equals and multiple hints
SELECT * FROM dbo.table4 WITH (INDEX = ix_table_id, FORCESEEK);

-- FORCESEEK alone
SELECT * FROM dbo.table5 WITH (FORCESEEK);

-- FORCESEEK with index and columns
SELECT * FROM dbo.table6 WITH (FORCESEEK (ix_table_id (column1, column2)));

-- Combined hints
SELECT * FROM dbo.table7 WITH (INDEX(ix_table_id), NOLOCK);

-- INDEX with numeric ID
SELECT * FROM dbo.table8 WITH (INDEX = 1);

-- INDEX with numeric ID in brackets
SELECT * FROM dbo.table9 WITH (INDEX(1, 2));
