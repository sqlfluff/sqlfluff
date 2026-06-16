CREATE OR REPLACE PROCEDURE test_sp1 (f1 int, f2 varchar(20))
AS $$
DECLARE
  min_val int;
BEGIN
  DROP TABLE IF EXISTS tmp_tbl;
  CREATE TEMP TABLE tmp_tbl(id int);
  INSERT INTO tmp_tbl values (f1),(10001),(10002);
  SELECT INTO min_val MIN(id) FROM tmp_tbl;
  RAISE INFO 'min_val = %, f2 = %', min_val, f2;
END;
$$ LANGUAGE plpgsql
SECURITY INVOKER;

CREATE OR REPLACE PROCEDURE test_sp2 (
    f1 IN int, f2 INOUT varchar(256), out_var OUT varchar(256)
)
AS $$
DECLARE
  loop_var int;
BEGIN
  IF f1 is null OR f2 is null THEN
    RAISE EXCEPTION 'input cannot be null';
  END IF;
  DROP TABLE if exists my_etl;
  CREATE TEMP TABLE my_etl(a int, b varchar);
    FOR loop_var IN 1..f1 LOOP
        insert into my_etl values (loop_var, f2);
        f2 := f2 || '+' || f2;
    END LOOP;
  SELECT INTO out_var count(*) from my_etl;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE test_sp_nonatomic ()
NONATOMIC
AS $$
BEGIN
    SELECT 1;
END;
$$ LANGUAGE plpgsql
SECURITY INVOKER;

CREATE PROCEDURE etl.test_sp_na (param1 int)
NONATOMIC
AS $$
BEGIN
    INSERT INTO test_table VALUES (param1);
    COMMIT;
    SELECT param1;
END;
$$ LANGUAGE plpgsql;

CREATE PROCEDURE test_set_config ()
AS $$
BEGIN
    SELECT 1;
END;
$$ LANGUAGE plpgsql
SET work_mem = '256MB';

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
