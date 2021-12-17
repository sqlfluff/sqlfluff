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

	--unreserved words
	all_pop.Language,
	ANSI_DEFAULTS ,
	ANSI_NULL_DFLT_OFF ,
	ANSI_NULL_DFLT_ON ,
	ANSI_NULLS ,
	ANSI_PADDING ,
	ANSI_WARNINGS ,
	ARITHABORT ,
	ARITHIGNORE ,
	CONCAT_NULL_YIELDS_NULL ,
	CURSOR_CLOSE_ON_COMMIT ,
	DATEFIRST ,
	DATEFORMAT ,
	DEADLOCK_PRIORITY ,
	DISK ,
	DUMP ,
	FIPS_FLAGGER ,
	FMTONLY ,
	FORCEPLAN ,
	IMPLICIT_TRANSACTIONS ,
	LOAD ,
	LOCK_TIMEOUT ,
	NOCOUNT ,
	NOEXEC ,
	NUMERIC_ROUNDABORT ,
	PARSEONLY ,
	PRECISION ,
	QUERY_GOVERNOR_COST_LIMIT ,
	QUOTED_IDENTIFIER ,
	REMOTE_PROC_TRANSACTIONS ,
	SECURITYAUDIT ,
	SHOWPLAN_ALL ,
	SHOWPLAN_TEXT ,
	SHOWPLAN_XML ,
	XACT_ABORT,

    ROW_NUMBER()OVER(PARTITION BY [EventNM], [PersonID] ORDER BY [DateofEvent] desc) AS [RN],
    RANK()OVER(PARTITION BY [EventNM] ORDER BY [DateofEvent] desc) AS [R],
    DENSE_RANK()OVER(PARTITION BY [EventNM] ORDER BY [DateofEvent] desc) AS [DR],
    NTILE(5)OVER(PARTITION BY [EventNM] ORDER BY [DateofEvent] desc) AS [NT],
	sum(t.col1) over (partition by t.col2, t.col3)

FROM dbo . all_pop	

