-- CREATE CONNECTION. https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-connection
CREATE CONNECTION c TYPE POSTGRESQL OPTIONS (host 'h', port '5432');

CREATE CONNECTION IF NOT EXISTS c TYPE POSTGRESQL OPTIONS (host 'h');

CREATE CONNECTION c TYPE POSTGRESQL OPTIONS (host 'h') COMMENT 'x';

CREATE CONNECTION c TYPE POSTGRESQL OPTIONS (a.b 'h');

CREATE CONNECTION c TYPE POSTGRESQL OPTIONS ('host' 'h');

CREATE CONNECTION c TYPE POSTGRESQL OPTIONS (user secret('secrets.r.us', 'u'), password secret('secrets.r.us', 'p'));

CREATE CONNECTION IF NOT EXISTS c TYPE HTTP OPTIONS (host 'https://slack.com', bearer_token secret('secrets.r.us', 't')) COMMENT 'slack';

CREATE SERVER c TYPE POSTGRESQL OPTIONS (host 'h');
