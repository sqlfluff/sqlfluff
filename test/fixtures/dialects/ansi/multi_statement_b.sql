# COMMENT
-- Another Comment
Select A from Sys.dual where a
-- inline comment
in  ('RED',  /* Inline */  'GREEN','BLUE');
select * from tbl_b; # as another comment
insert into sch.tbl_b
    (col1)
values (123);
with tmp as (
    select * from  blah
)
select a, b from tmp;
# And that's the end
