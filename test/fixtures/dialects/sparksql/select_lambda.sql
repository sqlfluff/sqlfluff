-- Lambda (higher-order function) arguments may use the strict-non-reserved
-- keywords `left` and `right` as variable names. See issue #5004.

-- The documented `array_sort` example from the Spark SQL function reference.
SELECT array_sort(
    array('bc', 'ab', 'dc'),
    (left, right) -> case
        when left is null and right is null then 0
        when left is null then -1
        when right is null then 1
        when left < right then 1
        when left > right then -1
        else 0
    end
);

-- Reserved-keyword lambda variables in a bracketed parameter list.
SELECT array_sort(my_arr, (left, right) -> left - right);

-- A single bare reserved-keyword lambda parameter.
SELECT transform(my_arr, left -> left + 1);

-- `left` and `right` are also usable as ordinary column identifiers.
SELECT left, right FROM my_table;
