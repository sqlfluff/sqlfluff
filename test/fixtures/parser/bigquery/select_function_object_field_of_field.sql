SELECT
  testFunction(a).b.c AS field_with_field,
  testFunction(a).b.* AS field_with_wildcard
FROM table1
