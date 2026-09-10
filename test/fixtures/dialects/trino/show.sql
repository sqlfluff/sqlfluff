SHOW FUNCTIONS;

SHOW FUNCTIONS FROM catalog_name.schema_name;

SHOW FUNCTIONS IN "catalog-name"."schema-name";

SHOW FUNCTIONS LIKE 'array%';

SHOW FUNCTIONS LIKE 'my$_function%' ESCAPE '$';

SHOW FUNCTIONS FROM catalog_name.schema_name LIKE 'my%';

SHOW FUNCTIONS IN catalog_name.schema_name LIKE 'my$_function%' ESCAPE '$';

SHOW STATS FOR motor;

SHOW STATS FOR delta.hm_iot_db.motor;

SHOW STATS FOR "catalog-name"."schema-name"."table-name";

SHOW STATS FOR (SELECT * FROM delta.hm_iot_db.motor WHERE voltage > 10);

SHOW STATS FOR (
    WITH readings AS (SELECT voltage FROM delta.hm_iot_db.motor)
    SELECT * FROM readings WHERE voltage > 10
);

SHOW STATS FOR (SELECT voltage FROM motor UNION ALL SELECT voltage FROM backup);

SHOW STATS FOR (VALUES (1), (2));
