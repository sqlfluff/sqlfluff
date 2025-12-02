select [1], [2], [3]
from
    table1 as t1
pivot
    (max(value) for rn in ([1], [2], [3]) ) as pvt;

select [1], [2], [3]
from
    table1 as t1
pivot
    (max(value) for rn in ([1], [2], [3]) ) pvt;
GO

SELECT
       unpvt.Program
     , dd.[Month Number] AS Month
FROM p
UNPIVOT (
	MonthValue FOR MonthColumn IN (Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec)
	) AS unpvt
INNER JOIN d
	ON [Month Name] = unpvt.MonthColumn;
GO
