-- LIST. https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-list
LIST 's3://us-east-1-dev/some_dir';

LIST 's3://us-east-1-dev/some_dir' WITH (CREDENTIAL aws_some_dir) LIMIT 2;
