update dbo.Cases
set [Flg] = 1
where ID in (select distinct [ID] from dbo.CX)
OPTION (Label = 'Cases') ;

update
	tt
set
	tt.rn += 1
from
	table1 as tt
join
	src
	on tt._id = src._id;

UPDATE stuff SET
  deleted = 1
OUTPUT DELETED.* INTO trash
WHERE useless = 1
