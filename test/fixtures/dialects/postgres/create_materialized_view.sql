CREATE MATERIALIZED VIEW my_mat_view AS
SELECT a
FROM my_table;

CREATE MATERIALIZED VIEW IF NOT EXISTS my_mat_view AS
SELECT a
FROM my_table;

CREATE MATERIALIZED VIEW my_mat_view AS
(
    SELECT a
    FROM my_table
);

CREATE MATERIALIZED VIEW my_mat_view AS
SELECT a
FROM my_table
WITH NO DATA;

CREATE MATERIALIZED VIEW my_mat_view AS
SELECT a
FROM my_table
WITH DATA;

CREATE MATERIALIZED VIEW IF NOT EXISTS my_mat_view AS
(
    SELECT a
    FROM my_table
);

CREATE MATERIALIZED VIEW my_mat_view AS
(
    SELECT
        a,
        b
    FROM
        my_table
    WHERE y = 'value'
);

CREATE MATERIALIZED VIEW IF NOT EXISTS my_mat_view AS
(
    SELECT
        a,
        b
    FROM
        my_table
    WHERE y = 'value'
);


CREATE MATERIALIZED VIEW my_mat_view AS
SELECT
    a,
    b
FROM
    my_table
WHERE y = 'value';

CREATE MATERIALIZED VIEW IF NOT EXISTS my_mat_view AS
SELECT
    a,
    b
FROM
    my_table
WHERE y = 'value';


CREATE MATERIALIZED VIEW my_mat_view AS
SELECT
    a,
    b
FROM
    my_table;

CREATE MATERIALIZED VIEW IF NOT EXISTS my_mat_view AS
SELECT
    a,
    b
FROM
    my_table;

-- SQL from issue #2039
CREATE MATERIALIZED VIEW bar
AS
(
    SELECT col
    FROM my_table
)
WITH NO DATA;

CREATE MATERIALIZED VIEW IF NOT EXISTS bar
AS
(
    SELECT col
    FROM my_table
)
WITH NO DATA;


CREATE MATERIALIZED VIEW my_mat_view
USING heap
WITH (prop_a = 1, prob_b = 'some_value', prop_c = FALSE, prop_d)
TABLESPACE pg_default
AS
(
    SELECT
        a,
        avg(b) AS my_avg,
        count(*) AS my_count
    FROM my_table
    GROUP BY grp
    HAVING col > 2
)
WITH DATA;

CREATE MATERIALIZED VIEW IF NOT EXISTS my_mat_view
USING heap
WITH (prop_a = 1, prob_b = 'some_value', prop_c = FALSE, prop_d)
TABLESPACE pg_default
AS
(
    SELECT
        a,
        avg(b) AS my_avg,
        count(*) AS my_count
    FROM my_table
    GROUP BY grp
    HAVING col > 2
)
WITH DATA;

CREATE MATERIALIZED VIEW my_mat_view
TABLESPACE pg_default
AS
SELECT
    table_1.field_1,
    table_1.field_2
FROM table_1
UNION
SELECT
    table_2.field_1,
    table_2.field_2
FROM table_2

ORDER BY field_1, field_2
WITH DATA;

CREATE MATERIALIZED VIEW my_mat_view
WITH (left.right)
AS
SELECT a
FROM my_table;

CREATE MATERIALIZED VIEW my_mat_view
WITH (opt1, opt2=5, opt3='str', ns.opt4, ns.opt5=6, ns.opt6='str', opt7=ASC)
AS
SELECT a
FROM my_table;

CREATE OR REPLACE MATERIALIZED VIEW my_mat_view AS
SELECT a
FROM my_table;
