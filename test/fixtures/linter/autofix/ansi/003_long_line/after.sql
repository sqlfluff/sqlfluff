SELECT
    GREATEST(1, 2 + 7, SQRT(a.long_variable_name_of_some_kind)) AS first_one,
    GREATEST(
        2 / 3.4322348982348,
        5 + 6,
        SQRT(a.nother_long_variable_name_of_some_kind)
    ) AS second_one
    FROM this_other_table
