-- definition is a column of sys.sql_modules, not a reserved keyword
SELECT definition
FROM sys.sql_modules
WHERE object_id = OBJECT_ID('dbo.usp_orders');

SELECT
    OBJECT_NAME(m.object_id) AS object_name,
    m.definition
FROM sys.sql_modules AS m
WHERE m.definition LIKE '%orders%';

SELECT definition AS object_definition
FROM sys.server_sql_modules;

CREATE TABLE dbo.rule_definitions (
    id INT NOT NULL,
    definition NVARCHAR(MAX) NULL
);

-- The permissions that use the keyword still parse
GRANT VIEW DEFINITION ON SCHEMA::dbo TO reporting;

GRANT VIEW ANY DEFINITION TO reporting;
