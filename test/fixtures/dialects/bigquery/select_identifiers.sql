--Identifiers can start with an underscore in BigQuery
-- and can contin just _ and 0-9
SELECT _01
FROM _2010_01;

--Identifiers can start with an underscore in BigQuery
-- and can contin just _ and 0-9
SELECT col_a AS _
FROM table1;

-- TODO: Currently we don't support this but should
-- Table names can contain dashes from FROM and TABLE clauses
-- But reluctant to add to general naked_identifier grammar and not
-- sure worth adding specific syntax for this unless someone requests it
-- https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical
-- SELECT * FROM data-customers-287.mydatabase.mytable;

-- Same as above but quoted
SELECT * FROM `data-customers-287`.mydatabase.mytable;
