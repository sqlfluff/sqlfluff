create view myview1 as 
select foo 
from bar;

create view myview2 
comment = 'just a comment' 
as 
select foo 
from bar
;

create view myview3 
(foo) 
as 
select foo from bar;

create view myview4 
(foo, baz) 
as 
select foo, baz 
from bar;

create view myview5 
(
    foo comment 'comment'
, baz comment 'comment'
) 
as 
select foo, baz 
from bar;

create or replace view myview6 
as 
select foo 
from bar;

create if not exists view myview7
as 
select foo 
from bar;