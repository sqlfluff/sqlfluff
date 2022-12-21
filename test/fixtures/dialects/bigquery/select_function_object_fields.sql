SELECT
  testFunction(a).b AS field,
  testFunction(a).* AS wildcard,
  testFunction(a).b.c AS field_with_field,
  testFunction(a).b.* AS field_with_wildcard,
  testFunction(a)[OFFSET(0)].* AS field_with_offset_wildcard,
  testFunction(a)[SAFE_OFFSET(0)].* AS field_with_safe_offset_wildcard,
  testFunction(a)[ORDINAL(1)].* AS field_with_ordinal_wildcard,
  testFunction(a)[ORDINAL(1)].a AS field_with_ordinal_field
FROM table1
