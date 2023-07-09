SELECT ARRAY[1,2] || ARRAY[3,4];

SELECT ARRAY[['meeting', 'lunch'], ['training', 'presentation']];

CREATE TABLE sal_emp (
    name            text,
    pay_by_quarter  integer[],
    schedule        text[][]
);

CREATE TABLE tictactoe (
    squares   integer[3][3]
);

SELECT * FROM sal_emp WHERE pay_by_quarter[1] = 10000 OR
                            pay_by_quarter[2] = 10000 OR
                            pay_by_quarter[3] = 10000 OR
                            pay_by_quarter[4] = 10000;

INSERT INTO sal_emp
    VALUES ('Bill',
    ARRAY[10000, 10000, 10000, 10000],
    ARRAY[['meeting', 'lunch'], ['training', 'presentation']]);

INSERT INTO sal_emp
    VALUES ('Carol',
    ARRAY[20000, 25000, 25000, 25000],
    ARRAY[['breakfast', 'consulting'], ['meeting', 'lunch']]);

SELECT name FROM sal_emp WHERE pay_by_quarter[1] <> pay_by_quarter[2];

SELECT schedule[1:2][1:1] FROM sal_emp WHERE name = 'Bill';

UPDATE sal_emp SET pay_by_quarter[4] = 15000
    WHERE name = 'Bill';

UPDATE sal_emp SET pay_by_quarter[1:2] = '{27000,27000}'
    WHERE name = 'Carol';

SELECT array_dims(ARRAY[1,2] || ARRAY[3,4,5]);

SELECT array_dims(ARRAY[1,2] || ARRAY[[3,4],[5,6]]);

SELECT ARRAY[1, 2] || '{3, 4}';

SELECT array_position(ARRAY['sun','mon','tue','wed','thu','fri','sat'], 'mon');

SELECT f1[1][-2][3] AS e1, f1[1][-1][5] AS e2
 FROM (SELECT '[1:1][-2:-1][3:5]={{{1,2,3},{4,5,6}}}'::int[] AS f1) AS ss;

SELECT '{Hello,World}'::_text AS text_array;

SELECT ARRAY['A', 'B', 'C']::_TEXT;

SELECT SUM(CASE
        WHEN direction = 'forward' THEN unit
        ELSE 0
        END
    ) * (MAX(ARRAY[id, vertical]))[2]
FROM direction_with_vertical_change;

-- More advanced cases with expressions and missing slice start/end when accessing

SELECT a[:], b[:1], c[2:], d[2:3];

SELECT a[1+2:3+4], b[5+6];
