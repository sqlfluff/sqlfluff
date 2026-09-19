-- A STRUCT field may carry a collation, between NOT NULL and the comment:
-- STRUCT < [fieldName [:] fieldType [NOT NULL] [COLLATE collationName]
--           [COMMENT str] [, ...] ] >
-- https://docs.databricks.com/aws/en/sql/language-manual/data-types/struct-type
CREATE TABLE t (s STRUCT<a: STRING COLLATE UTF8_BINARY>);

CREATE TABLE t (s STRUCT<a STRING COLLATE UTF8_LCASE>);

CREATE TABLE t (s STRUCT<a: STRING COLLATE UTF8_LCASE COMMENT 'field_comment'>);

CREATE TABLE t (s STRUCT<a: STRING NOT NULL COLLATE UTF8_LCASE>);

CREATE TABLE t (
    s STRUCT<a: STRING NOT NULL COLLATE UTF8_LCASE COMMENT 'field_comment'>
);

CREATE TABLE t (
    s STRUCT<a: STRING COLLATE UTF8_LCASE, b: STRING COLLATE DE, c: INT>
);

CREATE TABLE t (
    s STRUCT<a: STRUCT<b: STRING COLLATE UTF8_LCASE> COMMENT 'outer'>
);
