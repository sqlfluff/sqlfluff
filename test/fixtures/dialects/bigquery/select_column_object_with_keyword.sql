-- current is a reserved word but keywords are allowed as part of a nested object name
SELECT
  table1.current.column,
  table1.object.current.column,
  table1.object.nested.current.column,
FROM
  table1
