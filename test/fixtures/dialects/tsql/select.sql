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
		 WHEN 1 <   > 1 THEN 'False'
		 WHEN 1 !< 1 THEN 'Why is this a thing?'
		 WHEN 1 !
				 < 1 THEN 'Or this sort of thing?'
		 WHEN 1 != 1 THEN 'False'
		 WHEN 1 ! = 1 THEN 'False'
		 WHEN 1 !> 1 THEN 'NULL Handling, Probably'
		 WHEN 1 !  > 1 THEN 'NULL Handling, Probably'
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
	FIPS_FLAGGER ,
	FMTONLY ,
	FORCEPLAN ,
	IMPLICIT_TRANSACTIONS ,
	LOCK_TIMEOUT ,
	NOCOUNT ,
	NOEXEC ,
	NUMERIC_ROUNDABORT ,
	PARSEONLY ,
	PROPERTY ,
	QUERY_GOVERNOR_COST_LIMIT ,
	QUOTED_IDENTIFIER ,
	REMOTE_PROC_TRANSACTIONS ,
	SHOWPLAN_ALL ,
	SHOWPLAN_TEXT ,
	SHOWPLAN_XML ,
	XACT_ABORT,

	--TSQL non-keywords
	Rows,
	NaN,
	Rlike,
	Ilike,
	Separator,
	Auto_Increment,
	Unsigned,
	Describe,
	Comment,
	Ml,
	Modify,
	Minus,

    ROW_NUMBER()OVER(PARTITION BY [EventNM], [PersonID] ORDER BY [DateofEvent] desc) AS [RN],
    RANK()OVER(PARTITION BY [EventNM] ORDER BY [DateofEvent] desc) AS [R],
    DENSE_RANK()OVER(PARTITION BY [EventNM] ORDER BY [DateofEvent] desc) AS [DR],
    NTILE(5)OVER(PARTITION BY [EventNM] ORDER BY [DateofEvent] desc) AS [NT],
	sum(t.col1) over (partition by t.col2, t.col3),

	ROW_NUMBER() OVER (PARTITION BY (SELECT mediaty FROM dbo.MediaTypes ms WHERE ms.MediaTypeID = f.mediatypeid) ORDER BY AdjustedPriorityScore DESC) AS Subselect_Partition,

	ROW_NUMBER() OVER (PARTITION BY COALESCE(NPI1, NPI2) ORDER BY COALESCE(SystemEffectiveDTS1, SystemEffectiveDTS2) DESC) AS Coalesce_Partition,

	ROW_NUMBER() OVER (PARTITION BY (DayInMonth), (DaySuffix) ORDER BY Month ASC),
	COUNT(*) OVER (PARTITION BY NULL),

	[preceding]	= count(*) over(order by object_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW ),
	[central]	= count(*) over(order by object_id ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING ),
	[following]	= count(*) over(order by object_id ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING),

    EqualsAlias = ColumnName,
    OtherColumnName AS AsAlias,
	cast(1 as character varying(1)),
	cast([central] as int),

    --unbracketed functions
    CURRENT_TIMESTAMP,
    CURRENT_USER,
    SESSION_USER,
    SYSTEM_USER,
    USER,

    test(default, 2)


FROM dbo . all_pop;

SELECT DISTINCT TOP 5 some_value FROM some_table;

select
    'Tabellen' as Objekt,
    Count(*) as Anzahl
from dbo.sql_modules;

-- naked identifier with extended Unicode characters
select field1 AS 日期差多少天;


SELECT ID
FROM (
	SELECT TOP (1) ID FROM dbo.SomeTable ORDER BY ID
	UNION ALL
	SELECT TOP (1) ID FROM dbo.SomeTable ORDER BY ID DESC
) x;

SELECT $0 DollarAmt, $-1 NegAmt, -$.01 NegPenny, -+$-+$+++2 CrazyButValid;

SELECT ￡100 FWPoundAmt, ￠100 FWCent;
