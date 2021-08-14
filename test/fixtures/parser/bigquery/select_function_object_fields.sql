SELECT
  testFunction(a).b AS field,
  testFunction(a).* AS wildcard,
  testFunction(a).b.c AS field_with_field,
  testFunction(a).b.* AS field_with_wildcard,
  testFunction(a)[OFFSET(0)].* AS field_with_offset_wildcard
FROM table1
