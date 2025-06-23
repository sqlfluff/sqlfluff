SELECT
    test.d fourth_column,
    test.te AS fifth_column,
    first_column = test.a,
    second_column=test.b,
    third_column_long_name = (test.a + test.b) / 2
FROM foo AS test
