CREATE PROCEDURE execute_concatenated_string_with_variables ()
AS $$
BEGIN
    EXECUTE 'UPDATE tbl SET '
    || quote_ident(colname)
    || ' = '
    || quote_literal(newvalue)
    || ' WHERE key = '
    || quote_literal(keyvalue);
END;
$$ LANGUAGE plpgsql;

CREATE PROCEDURE execute_into ()
AS $$
DECLARE
    return_value string;
BEGIN
    EXECUTE 'SELECT 1' INTO return_value;
END;
$$ LANGUAGE plpgsql;

CREATE PROCEDURE execute_concatenated_string ()
AS $$
BEGIN
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
