CREATE TABLE example_dataset.example_table
(x INT64)
DEFAULT COLLATE 'und:ci';

CREATE OR REPLACE TABLE
example-project.example_dataset.example_table
(
  x INT64 OPTIONS(description="example"),
  y INT64 OPTIONS(description="example")
)
DEFAULT COLLATE 'und:ci'
CLUSTER BY x, y
OPTIONS(description="example");
