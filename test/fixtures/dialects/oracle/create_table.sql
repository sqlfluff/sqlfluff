-- create table with # in table name
create table tabl#e1 (c1 SMALLINT, c2 DATE);

-- create table with $ in table name
create table table1$ (c1 SMALLINT, c2 DATE);

-- create table with both $ & # in table name
create table tab#le1$ (c1 SMALLINT, c2 DATE);

-- create table with $ & # in column name
create table tab#le1$ (c#1 SMALLINT, c$2 DATE);
