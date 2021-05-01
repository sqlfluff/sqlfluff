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

CREATE TABLE table_with_table_comment_before_column_definition
COMMENT = 'table_with_table_comment_before_column_definition'
(
    column1 VARCHAR,
    column2 INTEGER
);

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

CREATE TABLE table_with_cluster_by_and_table_and_column_comments
COMMENT = 'table_with_comments'
(
    column1 VARCHAR COMMENT 'column1',
    column2 INTEGER
)
CLUSTER BY (column1);

CREATE TABLE table_with_cluster_by_with_function
(
    column1 TIMESTAMP COMMENT 'timestamp column',
    column2 INTEGER
)
CLUSTER BY (TO_DATE(column1), column2);

CREATE TABLE table_with_both_comments_and_cluster_by_with_function
(
    column1 TIMESTAMP COMMENT 'column comment',
    column2 INTEGER
)
COMMENT = 'table comment'
CLUSTER BY (TO_DATE(column1), column2);