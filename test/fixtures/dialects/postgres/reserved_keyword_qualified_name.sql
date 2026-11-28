-- A reserved keyword after the first part of a qualified name is an identifier.
-- https://github.com/sqlfluff/sqlfluff/issues/9332
create table my_schema.case (id char(18));

select my_schema.case.id from my_schema.case;

insert into my_schema.case (id) values ('a');

drop table my_schema.case;
