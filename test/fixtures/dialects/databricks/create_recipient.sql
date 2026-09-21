-- CREATE RECIPIENT. https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-recipient
CREATE RECIPIENT other_org;

CREATE RECIPIENT IF NOT EXISTS other_org;

CREATE RECIPIENT r USING ID 'azure:westus:abc';

CREATE RECIPIENT r COMMENT 'x';

CREATE RECIPIENT r PROPERTIES (k = 'v');

CREATE RECIPIENT r PROPERTIES (k 'v');

CREATE RECIPIENT r PROPERTIES (a.b = 'v');

CREATE RECIPIENT IF NOT EXISTS r USING ID 'x' COMMENT 'c' PROPERTIES (k = 'v', a.b 'w');
