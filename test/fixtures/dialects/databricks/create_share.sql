-- CREATE SHARE. https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-share
CREATE SHARE customer_share;

CREATE SHARE IF NOT EXISTS customer_share;

CREATE SHARE customer_share COMMENT 'x';

CREATE SHARE IF NOT EXISTS customer_share COMMENT 'x';
