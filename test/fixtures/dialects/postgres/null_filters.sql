-- Check nullability tests with standard and non-standard syntax
SELECT
    nullable_field IS NULL as standard_is_null,
    nullable_field ISNULL as non_standard_is_null,
    nullable_field IS NOT NULL as standard_not_null,
    nullable_field NOTNULL as non_standard_not_null
FROM
    t_test
WHERE
    nullable_field IS NULL OR
    nullable_field ISNULL OR
    nullable_field IS NOT NULL OR
    nullable_field NOTNULL
