-- Unit-looking identifiers are ordinary expressions in generic functions.
SELECT my_udf(year, 1), my_udf(day, month), my_udf(year), my_udf(d, y, m)
FROM t;

-- Quoted and qualified names do not dispatch to built-in date functions.
SELECT my_udf("year", t.day), analytics.my_udf(year, month),
    analytics.DATEADD(year, day, month), "DATEADD"(year, day, month),
    EXTRACT.my_udf(year, month)
FROM t;

-- Only the first argument is a date unit, including the supported aliases.
SELECT DATEADD(year, day, month), TIMEADD(dd, year, month),
    TIMESTAMPADD(ms, day, month), DATEDIFF(day, year, month),
    TIMEDIFF(hh, year, month), TIMESTAMPDIFF(ns, year, month),
    DATE_TRUNC(month, year), DATE_PART(year, day), EXTRACT(year, day)
FROM t;

-- FROM syntax and string date units keep their existing interpretation.
SELECT DATE_PART(year FROM day), EXTRACT(year FROM month),
    DATEADD('year', day, month), DATE_TRUNC('month', year),
    LAST_DAY(year), LAST_DAY(year, month), LAST_DAY(year, 'month')
FROM t;

-- Preserve TRUNC's date-unit slot; its numeric overload also accepts expressions.
SELECT TRUNC(year), TRUNC(year, scale), TRUNC(year, month), TRUNCATE(year, day),
    TRUNC(year, 'month'), TRUNCATE(year, 'day'),
    TIME_SLICE(day, year, 'month', 'END')
FROM t;

-- Retain named arguments, lambdas, aggregates and window suffixes.
SELECT my_udf(arg => year, other => month),
    ARRAY_TRANSFORM(month, x -> x + year),
    LISTAGG(year, ',') WITHIN GROUP (ORDER BY month),
    SUM(year) OVER (PARTITION BY month)
FROM t;
