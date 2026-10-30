explain select 1;

explain update tbl set foo = 1 where bar = 2;

explain delete from tbl where foo = 1;

explain insert into tbl (col1) values (123);

explain replace into tbl (col1) values (123);

explain tbl;

describe tbl;

desc tbl col1;

describe tbl 'col%';

describe select 1;

explain format = json select 1;

explain format=tree select * from tbl;

explain format = traditional select 1;

explain analyze select * from tbl;

explain analyze format = tree select 1;

explain format = json into @plan select 1;

explain for connection 4;

explain format = json for connection 4;

describe tbl col1;

explain for schema db1 select * from tbl;

explain format = json for database db1 select 1;
