CREATE OR REPLACE TABLE foo
OPTIONS
  (description = 'copy of bar') AS (
    SELECT * from bar
    )
