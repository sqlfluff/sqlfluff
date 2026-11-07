-- GEOGRAPHY and GEOMETRY types.
-- https://docs.databricks.com/aws/en/sql/language-manual/data-types/geography-type
-- https://docs.databricks.com/aws/en/sql/language-manual/data-types/geometry-type
CREATE TABLE t (g GEOGRAPHY(4326), h GEOGRAPHY(ANY));

CREATE TABLE t (g GEOMETRY(4326), h GEOMETRY(ANY));

SELECT CAST(x AS GEOGRAPHY(4326)), CAST(y AS GEOMETRY(ANY));
