update dbo.Cases
set [Flg] = 1
where ID in (select distinct [ID] from dbo.CX)
OPTION (Label = 'Cases') ;
