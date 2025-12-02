CREATE OR REPLACE PROCEDURE create_account
(
    _account_uuid UUID
)
AS
$$
BEGIN
    RETURN;
END;
$$ LANGUAGE plpgsql;

CREATE PROCEDURE insert_data(a integer, b integer)
LANGUAGE SQL
AS $$
INSERT INTO tbl VALUES (a);
INSERT INTO tbl VALUES (b);
$$;

CREATE PROCEDURE abc.cdf()
LANGUAGE sql
BEGIN ATOMIC
WITH tbl2 AS (
SELECT a.apple
FROM tbl1 a
)

SELECT t.apple
FROM tbl2 t
;
END;
