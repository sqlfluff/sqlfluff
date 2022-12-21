CREATE VIEW IF NOT EXISTS a
AS
    SELECT
        c
    FROM table1
    INNER JOIN table2 ON (table1.id = table2.id)
