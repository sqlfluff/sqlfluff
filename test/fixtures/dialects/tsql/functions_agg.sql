SELECT
	string_agg(t.v, '; ') within group (order by v) as column_name1
	,PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY t.Rate)
                            OVER (PARTITION BY Name) AS MedianCont
	,PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY t.Rate)
                            OVER (PARTITION BY Name) AS MedianDisc
from
	table1 t
group by
	employee_id
HAVING MIN([ArrivalDt]) <= MAX([DischargeDt])

DROP TABLE #Mercury;
