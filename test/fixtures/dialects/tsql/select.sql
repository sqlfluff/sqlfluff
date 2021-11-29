--For testing valid select clause elements
SELECT
	CASE WHEN 1 = 1 THEN 'True'
		 WHEN 1 > 1 THEN 'False'
		 WHEN 1 < 1 THEN 'False'
		 WHEN 1 >= 1 THEN 'True'
		 WHEN 1 > = 1 THEN 'True'
		 WHEN 1 <= 1 THEN 'True'
		 WHEN 1 <	= 1 THEN 'True'
		 WHEN 1 <> 1 THEN 'False'
		 WHEN 1 !< 1 THEN 'Why is this a thing?'
		 WHEN 1 !
				 < 1 THEN 'Or this sort of thing?'
		 WHEN 1 != 1 THEN 'False'
		 WHEN 1 !> 1 THEN 'NULL Handling, Probably'
		 ELSE 'Silly Tests'
	END,
	all_pop. [Arrival Date],
	all_pop.Row#,
	all_pop.b@nanas,
	[# POAs],
	'TSQLs escaping quotes test',
	'TSQL''s escaping quotes test',
	'TSQL' 's escaping quotes test',
	'TSQL' AS 's escaping quotes test',
	'',
	'''',
    ROW_NUMBER()OVER(PARTITION BY [EventNM], [PersonID] ORDER BY [DateofEvent] desc) AS [RN],
    RANK()OVER(PARTITION BY [EventNM] ORDER BY [DateofEvent] desc) AS [R],
    DENSE_RANK()OVER(PARTITION BY [EventNM] ORDER BY [DateofEvent] desc) AS [DR],
    NTILE(5)OVER(PARTITION BY [EventNM] ORDER BY [DateofEvent] desc) AS [NT],
	sum(t.col1) over (partition by t.col2, t.col3)

FROM dbo . all_pop	

