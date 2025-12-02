ALTER DATABASE inventory SET DBPROPERTIES (
    'Edited-by' = 'John'
);

ALTER DATABASE inventory SET DBPROPERTIES (
    'Edited-by' = 'John',
    'Edit-date' = '01/01/2001'
);

ALTER SCHEMA inventory SET DBPROPERTIES (
    'Edited-by' = 'John'
);

ALTER SCHEMA inventory SET DBPROPERTIES (
    'Edited-by' = 'John',
    'Edit-date' = '01/01/2001'
);

ALTER DATABASE inventory SET LOCATION 'file:/temp/spark-warehouse/new_inventory.db';
ALTER SCHEMA inventory SET LOCATION 'file:/temp/spark-warehouse/new_inventory.db';
