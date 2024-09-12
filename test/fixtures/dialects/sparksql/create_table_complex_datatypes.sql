--Create Table with complex datatypes
CREATE TABLE table_identifier
( a STRUCT<b: STRING, c: BOOLEAN>, d MAP<STRING, BOOLEAN>, e ARRAY<STRING>);

--Create Table with complex datatypes and comments
CREATE TABLE table_identifier
( a STRUCT<b: STRING COMMENT 'struct_comment', c: BOOLEAN> COMMENT 'col_comment', d MAP<STRING, BOOLEAN> COMMENT 'col_comment', e ARRAY<STRING> COMMENT 'col_comment');

--Create Table with nested complex datatypes
CREATE TABLE table_identifier
( a STRUCT<b: STRING, c: MAP<STRING, BOOLEAN>>, d MAP<STRING, STRUCT<e: STRING, f: MAP<STRING, BOOLEAN>>>, g ARRAY<STRUCT<h: STRING, i: MAP<STRING, BOOLEAN>>>);

--Create Table with complex datatypes and quoted identifiers
CREATE TABLE table_identifier
( a STRUCT<`b`: STRING, c: BOOLEAN>, `d` MAP<STRING, BOOLEAN>, e ARRAY<STRING>);


CREATE TABLE my_table (
    field_a STRING,
    field_b VARIANT
);
