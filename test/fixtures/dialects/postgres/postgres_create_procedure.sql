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
