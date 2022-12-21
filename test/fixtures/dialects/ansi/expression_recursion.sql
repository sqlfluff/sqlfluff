 -- This test checks for recursion errors. If the expression
 -- is not parsed correctly it can lead to very deep recursion.

 -- If this test is failing, then check the structure of expression
 -- parsing.

 select
        1
    from
        test_table
    where
        test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%' --5
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%' -- 10
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%' -- 15
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%' -- 20
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%' --30
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%'
        or test_table.string_field like 'some string%' -- 40
