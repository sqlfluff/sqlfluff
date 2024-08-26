-- ALTER TABLE examples from Databricks documentation
-- https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-alter-view.html

ALTER VIEW tempsc1.v1 RENAME TO tempsc1.v2;

ALTER VIEW tempsc1.v2 SET TBLPROPERTIES ('created.by.user' = "John", 'created.date' = '01-01-2001' );

ALTER VIEW tempsc1.v2 UNSET TBLPROPERTIES (`created`.`by`.`user`, created.date);

ALTER VIEW tempsc1.v2 AS SELECT * FROM tempsc1.v1;

ALTER VIEW v1 OWNER TO `alf@melmak.et`;

ALTER VIEW v1 SET OWNER TO `alf@melmak.et`;

ALTER VIEW v1 WITH SCHEMA BINDING;
ALTER VIEW v1 WITH SCHEMA COMPENSATION;
ALTER VIEW v1 WITH SCHEMA TYPE EVOLUTION;
ALTER VIEW v1 WITH SCHEMA EVOLUTION;

ALTER MATERIALIZED VIEW my_mv
    ADD SCHEDULE CRON '0 0 0 * * ? *' AT TIME ZONE 'America/Los_Angeles';

ALTER MATERIALIZED VIEW my_mv
    ALTER SCHEDULE CRON '0 0/15 * * * ? *';

ALTER MATERIALIZED VIEW my_mv
    DROP SCHEDULE;

ALTER VIEW test SET TAGS ('tag1' = 'val1', 'tag2' = 'val2', 'tag3' = 'val3');

ALTER VIEW test UNSET TAGS ('tag1', 'tag2', 'tag3');
