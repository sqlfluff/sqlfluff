-- https://docs.vertica.com/latest/en/sql-reference/statements/create-statements/create-table/#examples
-- Some functionality isn't covered yet, so I commented it

CREATE TABLE public.Premium_Customer
(
    ID IDENTITY,
    lname varchar(25),
    fname varchar(25),
    store_membership_card int
);

CREATE TABLE orders(
    orderkey    INT ENCODING AUTO,
    custkey     INT,
    prodkey     ARRAY[VARCHAR(10)],
    orderprices ARRAY[DECIMAL(12,2)],
    orderdate   DATE
);

CREATE TABLE orders(
    orderkey    INT ENCODING AUTO,
    custkey     INT,
    prodkey     ARRAY[VARCHAR(10)],
    orderprices ARRAY[DECIMAL(12,2)],
    orderdate   DATE
)
partition by orderdate::date group by CALENDAR_HIERARCHY_DAY(orderdate::DATE, 3, 2) REORGANIZE;

-- CREATE TABLE inventory
-- (store INT, products ROW(name VARCHAR, code VARCHAR));

CREATE TEMPORARY TABLE tempDelete (a int, b int);

CREATE TEMPORARY TABLE tempPreserve (a int, b int) ON COMMIT PRESERVE ROWS;
