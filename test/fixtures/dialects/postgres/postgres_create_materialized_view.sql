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
TABLESPACE pg_default
WITH (prop_a = 1, prob_b = 'some_value', prop_c = FALSE, prop_d)
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
TABLESPACE pg_default
WITH (prop_a = 1, prob_b = 'some_value', prop_c = FALSE, prop_d)
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
