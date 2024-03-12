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

-- CREATE TABLE inventory
-- (store INT, products ROW(name VARCHAR, code VARCHAR));

CREATE TEMPORARY TABLE tempDelete (a int, b int);

CREATE TEMPORARY TABLE tempPreserve (a int, b int) ON COMMIT PRESERVE ROWS;

CREATE TABLE orders (
    orderkey    INT ENCODING AUTO,
    custkey     INT,
    prodkey     ARRAY[VARCHAR(10)],
    orderprices ARRAY[DECIMAL(12,2)],
    orderdate   DATE
)
partition by orderdate::date group by CALENDAR_HIERARCHY_DAY(orderdate::date, 1, 1);

CREATE TABLE orders (
    orderkey    INT ENCODING AUTO,
    custkey     INT,
    prodkey     ARRAY[VARCHAR(10)],
    orderprices ARRAY[DECIMAL(12,2)],
    orderdate   DATE
)
partition by (
    concat(
        ((date_part('year', (orderdate)::timestamp))::int)::varchar,
        ((date_part('month', (orderdate)::timestamp))::int)::varchar
    )
);

CREATE TABLE orders (
    orderkey    INT ENCODING AUTO,
    custkey     INT,
    orderdate   DATE
)
partition by orderdate::date
group by
    (
        case
            when
                (datediff('year', orderdate::date, ((now())::timestamptz(6))::date) >= 2)
                then (date_trunc('year', orderdate::date))::date
            when
                (datediff('month', orderdate::date, ((now())::timestamptz(6))::date) >= 2)
                then (date_trunc('month', orderdate::date))::date
            else orderdate::date
        end
    );
