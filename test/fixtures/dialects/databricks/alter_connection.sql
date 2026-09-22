-- ALTER CONNECTION. https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-connection
ALTER CONNECTION c SET OWNER TO `u`;

ALTER CONNECTION c RENAME TO d;

ALTER CONNECTION c OPTIONS (host 'h');

ALTER CONNECTION c OPTIONS (user secret('s', 'u'));
