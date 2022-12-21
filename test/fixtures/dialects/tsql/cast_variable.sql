DECLARE @DateNow date = ISNULL(Shared.GetESTDateTime(GETDATE()), GETDATE())

select enc.personid as personid,
				 cast('1900-01-01' as datetime2(7)) as DataRefreshDate
from encounter enc;

 declare @sample nvarchar(max) = cast(100 as nvarchar(max))
