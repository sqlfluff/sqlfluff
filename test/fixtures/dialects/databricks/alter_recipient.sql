-- ALTER RECIPIENT. https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-recipient
ALTER RECIPIENT r RENAME TO s;

ALTER RECIPIENT r SET PROPERTIES ('country' = 'US');

ALTER RECIPIENT r SET PROPERTIES (a.b 'v');

ALTER RECIPIENT r UNSET PROPERTIES ('country');

ALTER RECIPIENT r OWNER TO `u`;
