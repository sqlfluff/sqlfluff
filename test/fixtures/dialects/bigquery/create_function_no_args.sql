CREATE FUNCTION add() RETURNS integer
    AS 'select $1 + $2;'
    LANGUAGE SQL;

DROP FUNCTION myproject.mydataset.addfunc;
