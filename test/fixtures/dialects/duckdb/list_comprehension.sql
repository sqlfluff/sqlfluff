SELECT [lower(x) FOR x IN strings]
FROM (VALUES (['Hello', '', 'World'])) t(strings);

SELECT [upper(x) FOR x IN strings IF len(x) > 0]
FROM (VALUES (['Hello', '', 'World'])) t(strings);

SELECT [x + i FOR x, i IN [4, 5, 6]];

SELECT [4, 5, 6] AS l, [x FOR x, i IN l IF i != 2] AS filtered;

SELECT [i FOR x, i IN [4, 5, 6]];

select ["value" + "position" for "value", "position" in [4, 5, 6]];
