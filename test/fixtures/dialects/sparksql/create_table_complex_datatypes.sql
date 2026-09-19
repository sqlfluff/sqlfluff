--Create Table with complex datatypes
CREATE TABLE table_identifier
( a STRUCT<b: STRING, c: BOOLEAN>, d MAP<STRING, BOOLEAN>, e ARRAY<STRING>);

--Create Table with complex datatypes without : in struct
CREATE TABLE table_identifier
( a STRUCT<b STRING, c BOOLEAN>, d MAP<STRING, BOOLEAN>, e ARRAY<STRING>);

--Create Table with complex datatypes and comments
CREATE TABLE table_identifier
( a STRUCT<b: STRING COMMENT 'struct_comment', c: BOOLEAN> COMMENT 'col_comment', d MAP<STRING, BOOLEAN> COMMENT 'col_comment', e ARRAY<STRING> COMMENT 'col_comment');

--Create Table with nested complex datatypes
CREATE TABLE table_identifier
( a STRUCT<b: STRING, c: MAP<STRING, BOOLEAN>>, d MAP<STRING, STRUCT<e: STRING, f: MAP<STRING, BOOLEAN>>>, g ARRAY<STRUCT<h: STRING, i: MAP<STRING, BOOLEAN>>>);

--Create Table with nested complex datatypes without : in struct
CREATE TABLE table_identifier
( a STRUCT<b STRING, c MAP<STRING, BOOLEAN>>, d MAP<STRING, STRUCT<e STRING, f MAP<STRING, BOOLEAN>>>, g ARRAY<STRUCT<h STRING, i MAP<STRING, BOOLEAN>>>);


--Create Table with complex datatypes and quoted identifiers
CREATE TABLE table_identifier
( a STRUCT<`b`: STRING, c: BOOLEAN>, `d` MAP<STRING, BOOLEAN>, e ARRAY<STRING>);


CREATE TABLE my_table (
    field_a STRING,
    field_b VARIANT
);

--Create Table with NOT NULL on a struct field
--https://spark.apache.org/docs/latest/sql-ref-datatypes.html
CREATE TABLE table_identifier
( a STRUCT<b: STRING NOT NULL, c: BOOLEAN>);

--Create Table with NOT NULL on a struct field written without :
CREATE TABLE table_identifier
( a STRUCT<b STRING NOT NULL>);

--Create Table with NOT NULL before a struct field comment
CREATE TABLE table_identifier
( a STRUCT<b: STRING NOT NULL COMMENT 'struct_comment'>);

--Create Table with NOT NULL on a nested struct field
CREATE TABLE table_identifier
( a STRUCT<b: STRUCT<c: STRING NOT NULL> NOT NULL>);
