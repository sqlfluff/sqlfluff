CREATE PROCEDURE execute_within_stored_procedure_dummy()
AS $$
BEGIN
    EXECUTE 'UPDATE tbl SET '
    || quote_ident(colname)
    || ' = '
    || quote_literal(newvalue)
    || ' WHERE key = '
    || quote_literal(keyvalue);

    EXECUTE 'SELECT 1' INTO return_value;

    -- Pulled from GitHub issue: https://github.com/sqlfluff/sqlfluff/issues/7798
    EXECUTE '
        CREATE TEMP TABLE xxxxx AS ( 
        SELECT columns
        FROM "schema".table this_table
        WHERE this_table.column IN ( 
            ' || concatenated_string || '
        )
    )';
END;
$$ LANGUAGE plpgsql;