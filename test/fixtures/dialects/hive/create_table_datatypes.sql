CREATE TABLE db.foo (
    col1 string,
    col2 int,
    col3 decimal,
    col4 decimal(10, 2),
    col5 ARRAY<double>,
    col6 MAP<varchar, date>,
    col7 STRUCT< field1: boolean, field2: ARRAY<double precision>, field3: UNIONTYPE<string, decimal(10, 2)>>,
    col8 UNIONTYPE<string, ARRAY<char>>
);
