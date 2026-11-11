-- The parentheses are required; the parameter list inside them may be empty.
CREATE OR REPLACE PROCEDURE main.dbo.usp_refresh()
LANGUAGE SQL
AS
BEGIN
    DELETE FROM main.dbo.employees WHERE first_name IS NULL;
END;
