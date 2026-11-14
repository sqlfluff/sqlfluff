CREATE SCHEMA staging
    CREATE TABLE test (id INT);
GO

CREATE SCHEMA reporting AUTHORIZATION dbo
    GRANT SELECT ON SCHEMA::reporting TO reader
    CREATE TABLE source (id INT)
    -- A view and permissions belong to the same atomic schema definition.
    CREATE VIEW source_view AS SELECT id FROM source
    DENY UPDATE ON SCHEMA::reporting TO reader
    REVOKE DELETE ON SCHEMA::reporting FROM reader;
GO

CREATE SCHEMA multiple_tables
    CREATE TABLE first_table (id INT)
    CREATE TABLE second_table (id INT);
GO

CREATE SCHEMA graph_data
    CREATE TABLE graph_data.Person (id INT) AS NODE
    CREATE TABLE graph_data.Relation (id INT) AS EDGE
    CREATE TABLE likes AS EDGE
    CREATE TABLE regular (id INT);
GO

CREATE SCHEMA separate;
CREATE TABLE independent (id INT);
GO
