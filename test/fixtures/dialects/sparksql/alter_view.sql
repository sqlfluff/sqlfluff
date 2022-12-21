-- RENAME View
ALTER VIEW view_identifier RENAME TO view_identifier;
ALTER VIEW tempdb1.v1 RENAME TO tempdb1.v2;

--SET View Properties
ALTER VIEW view_identifier SET TBLPROPERTIES ( "property_key" = "property_val");
ALTER VIEW tempdb1.v2 SET TBLPROPERTIES (
    'created.by.user' = "John", 'created.date' = '01-01-2001'
);

--UNSET View Properties
ALTER VIEW view_identifier UNSET TBLPROPERTIES ( "property_key");
ALTER VIEW view_identifier UNSET TBLPROPERTIES IF EXISTS ( "property_key");
ALTER VIEW tempdb1.v2 UNSET TBLPROPERTIES ('created.by.user', 'created.date');

--ALTER View AS SELECT
ALTER VIEW view_identifier AS (
    SELECT
        a,
        b
    FROM tempdb1.v1
);

ALTER VIEW tempdb1.v2 AS
SELECT
    a,
    b
FROM tempdb1.v1;
