CREATE TABLE basic_table (
    column1 VARCHAR,
    column2 INTEGER
);

CREATE TABLE basic_table_with_column_comment (
    column1 VARCHAR COMMENT 'column1 desc',
    column2 INTEGER
);

CREATE TABLE table_with_table_comment (
    column1 VARCHAR,
    column2 INTEGER
)
COMMENT = 'table_with_comments';

CREATE TABLE table_with_table_and_column_comments (
    column1 VARCHAR COMMENT 'column1 desc',
    column2 INTEGER
)
COMMENT = 'table_with_comments';

CREATE TABLE table_with_cluster_by (
    column1 VARCHAR,
    column2 INTEGER
)
CLUSTER BY (column1);

CREATE TABLE table_with_cluster_by_and_table_comment (
    column1 VARCHAR,
    column2 INTEGER
)
CLUSTER BY (column1)
COMMENT = 'table_with_comments';

CREATE TABLE table_with_cluster_by_and_table_and_column_comments (
    column1 VARCHAR COMMENT 'column1 desc',
    column2 INTEGER
)
CLUSTER BY (column1)
COMMENT = 'table_with_comments';
