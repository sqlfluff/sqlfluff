SELECT [lower(x) FOR x IN strings]
FROM (VALUES (['Hello', '', 'World'])) t(strings);

SELECT [upper(x) FOR x IN strings IF len(x) > 0]
FROM (VALUES (['Hello', '', 'World'])) t(strings);
