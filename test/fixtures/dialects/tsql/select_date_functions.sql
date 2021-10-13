SELECT
    [hello],
    DATEDIFF(day, [mydate], GETDATE()) AS [test],
    DATEPART(day, [mydate], GETDATE()) AS [test2],
    DATEDIFF(year,        '2005-12-31 23:59:59.9999999', '2006-01-01 00:00:00.0000000'),
    DATEDIFF(quarter,     '2005-12-31 23:59:59.9999999', '2006-01-01 00:00:00.0000000'),
    DATEDIFF(month,       '2005-12-31 23:59:59.9999999', '2006-01-01 00:00:00.0000000'),
    DATEDIFF(dayofyear,   '2005-12-31 23:59:59.9999999', '2006-01-01 00:00:00.0000000'),
    DATEDIFF(day,         '2005-12-31 23:59:59.9999999', '2006-01-01 00:00:00.0000000'),
    DATEDIFF(week,        '2005-12-31 23:59:59.9999999', '2006-01-01 00:00:00.0000000'),
    DATEDIFF(hour,        '2005-12-31 23:59:59.9999999', '2006-01-01 00:00:00.0000000'),
    DATEDIFF(minute,      '2005-12-31 23:59:59.9999999', '2006-01-01 00:00:00.0000000'),
    DATEDIFF(second,      '2005-12-31 23:59:59.9999999', '2006-01-01 00:00:00.0000000'),
    DATEDIFF(millisecond, '2005-12-31 23:59:59.9999999', '2006-01-01 00:00:00.0000000'),
    DATEDIFF(microsecond, '2005-12-31 23:59:59.9999999', '2006-01-01 00:00:00.0000000'),
    DATEADD(year,2147483647, '20060731'),
    DATEADD(year,-2147483647, '20060731'),
    DATENAME(year, '12:10:30.123'),
    DATENAME(month, '12:10:30.123'),
    DATENAME(day, '12:10:30.123'),
    DATENAME(dayofyear, '12:10:30.123'),
    DATENAME(weekday, '12:10:30.123')
FROM
    mytable;
