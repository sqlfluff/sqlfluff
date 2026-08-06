-- Column list aliases on table-valued expressions (issue #6733).
SELECT r.c.value('column[1]', 'varchar(10)') AS [Value]
FROM @xml.nodes('/rows/row') AS r(c);

-- The spaced form parses identically.
SELECT t.c.query('.')
FROM @x.nodes('/Root/row') AS t (c);

-- Multi-column list, without AS.
SELECT na.Loc.query('.')
FROM SomeTable
CROSS APPLY SomeXMLColumn.nodes('/root/Location') na(Loc, Other);

-- The VALUES clause column alias list goes through the same segment, which
-- is what the ANSI grammar named this slot for in the first place.
SELECT a, b
FROM (VALUES (1, 2), (3, 4)) AS t(a, b);
