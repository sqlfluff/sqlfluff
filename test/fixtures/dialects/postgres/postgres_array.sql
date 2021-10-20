SELECT ARRAY[1,2] || ARRAY[3,4];

CREATE TABLE sal_emp (
    name            text,
    pay_by_quarter  integer[],
    schedule        text[][]
);

CREATE TABLE tictactoe (
    squares   integer[3][3]
);
