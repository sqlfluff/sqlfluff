-- Test qualifying datatype with schema
CREATE TABLE counters (
    my_type public.MY_TYPE
);

--CREATE TABLE films (
--    code        char(5) CONSTRAINT firstkey PRIMARY KEY,
--    title       varchar(40) NOT NULL,
--    did         integer NOT NULL,
--    date_prod   date,
--    kind        varchar(10),
--    len         interval hour to minute
--);

CREATE TABLE distributors (
     did    integer PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
     name   varchar(40) NOT NULL CHECK (name <> '')
);

--CREATE TABLE array_int (
--    vector  int[][]
--);

--CREATE TABLE films (
--    code        char(5),
--    title       varchar(40),
--    did         integer,
--    date_prod   date,
--    kind        varchar(10),
--    len         interval hour to minute,
--    CONSTRAINT production UNIQUE(date_prod)
--);

CREATE TABLE distributors (
    did     integer CHECK (did > 100),
    name    varchar(40)
);

CREATE TABLE distributors (
    did     integer,
    name    varchar(40),
    CONSTRAINT con1 CHECK (did > 100 AND name <> '')
);

--CREATE TABLE films (
--    code        char(5),
--    title       varchar(40),
--    did         integer,
--    date_prod   date,
--    kind        varchar(10),
--    len         interval hour to minute,
--    CONSTRAINT code_title PRIMARY KEY(code,title)
--);

CREATE TABLE distributors (
    did     integer,
    name    varchar(40),
    PRIMARY KEY(did)
);

CREATE TABLE distributors (
    did     integer PRIMARY KEY,
    name    varchar(40)
);

CREATE TABLE distributors (
    name      varchar(40) DEFAULT 'Luso Films',
    did       integer DEFAULT nextval('distributors_serial'),
    modtime   timestamp DEFAULT current_timestamp
);

CREATE TABLE distributors (
    did     integer CONSTRAINT no_null NOT NULL,
    name    varchar(40) NOT NULL
);

CREATE TABLE distributors (
    did     integer,
    name    varchar(40) UNIQUE
);

CREATE TABLE distributors (
    did     integer,
    name    varchar(40),
    UNIQUE(name)
);

CREATE TABLE distributors (
    did     integer,
    name    varchar(40),
    UNIQUE(name) WITH (fillfactor=70)
)
WITH (fillfactor=70);

--CREATE TABLE circles (
--    c circle,
--    EXCLUDE USING gist (c WITH &&)
--);

CREATE TABLE cinemas (
        id serial,
        name text,
        location text
) TABLESPACE diskvol1;

CREATE TYPE employee_type AS (name text, salary numeric);

CREATE TABLE employees OF employee_type (
    PRIMARY KEY (name),
    salary WITH OPTIONS DEFAULT 1000
);

CREATE TABLE measurement (
    logdate         date not null,
    peaktemp        int,
    unitsales       int
) PARTITION BY RANGE (logdate);

CREATE TABLE measurement_year_month (
    logdate         date not null,
    peaktemp        int,
    unitsales       int
) PARTITION BY RANGE (EXTRACT(YEAR FROM logdate), EXTRACT(MONTH FROM logdate));

CREATE TABLE cities (
    city_id      bigserial not null,
    name         text not null,
    population   bigint
) PARTITION BY LIST (left(lower(name), 1));

CREATE TABLE orders (
    order_id     bigint not null,
    cust_id      bigint not null,
    status       text
) PARTITION BY HASH (order_id);

CREATE TABLE measurement_y2016m07
    PARTITION OF measurement (
    unitsales DEFAULT 0
) FOR VALUES FROM ('2016-07-01') TO ('2016-08-01');

CREATE TABLE measurement_ym_older
    PARTITION OF measurement_year_month
    FOR VALUES FROM (MINVALUE, MINVALUE) TO (2016, 11);

CREATE TABLE measurement_ym_y2016m11
    PARTITION OF measurement_year_month
    FOR VALUES FROM (2016, 11) TO (2016, 12);

CREATE TABLE measurement_ym_y2016m12
    PARTITION OF measurement_year_month
    FOR VALUES FROM (2016, 12) TO (2017, 01);

CREATE TABLE measurement_ym_y2017m01
    PARTITION OF measurement_year_month
    FOR VALUES FROM (2017, 01) TO (2017, 02);

CREATE TABLE cities_ab
    PARTITION OF cities (
    CONSTRAINT city_id_nonzero CHECK (city_id != 0)
) FOR VALUES IN ('a', 'b');

CREATE TABLE cities_ab
    PARTITION OF cities (
    CONSTRAINT city_id_nonzero CHECK (city_id != 0)
) FOR VALUES IN ('a', 'b') PARTITION BY RANGE (population);

CREATE TABLE cities_ab_10000_to_100000
    PARTITION OF cities_ab FOR VALUES FROM (10000) TO (100000);

CREATE TABLE orders_p1 PARTITION OF orders
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE orders_p2 PARTITION OF orders
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE orders_p3 PARTITION OF orders
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE orders_p4 PARTITION OF orders
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);

CREATE TABLE cities_partdef
    PARTITION OF cities DEFAULT;

CREATE UNLOGGED TABLE staging (
    event_type INTEGER
    , event_time TIMESTAMP
    , user_email VARCHAR
    , phone_number VARCHAR
    , processing_date DATE
    , PRIMARY KEY (event_type, event_time, user_email, phone_number, processing_date)
);

CREATE TABLE measurement (
city_id int NOT NULL,
logdate date NOT NULL,
peaktemp int,
unitsales int
) PARTITION BY RANGE (logdate);

CREATE TABLE public.public (
id serial NOT NULL,
name text NOT NULL,
group_name text NULL,
cluster_id int8 NULL,
date_created timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
date_updated timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
operation_id int4 NOT NULL DEFAULT '-1'::integer
);

CREATE TABLE main.test_table (
    "col1" character varying(40) NOT NULL,
    "col2" double precision
);

CREATE TABLE groups (
    group_id INTEGER PRIMARY KEY generated BY DEFAULT AS IDENTITY
);

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY generated BY DEFAULT AS IDENTITY,
    group_id INTEGER REFERENCES groups (group_id) ON DELETE CASCADE,
    domain_id INTEGER REFERENCES groups (group_id) ON UPDATE RESTRICT,
    other_id INTEGER REFERENCES groups (group_id) MATCH SIMPLE
);

CREATE TABLE orders
(
id bigint NOT NULL DEFAULT NEXTVAL('orders_id_seq'::regclass),
constraint_collate_constraints text UNIQUE COLLATE numeric NOT NULL PRIMARY KEY,
constraints_collate text NOT NULL UNIQUE COLLATE numeric,
collate_constraints text COLLATE numeric NOT NULL UNIQUE
);


-- Use non-reserved `usage` word as a table identifier
CREATE TABLE IF NOT EXISTS quotas.usage(foo int);

-- Use non-reserved `usage` word as a column identifier
CREATE TABLE IF NOT EXISTS quotas.my_table(usage int);

-- NOT NULL both before and after a default constraint
CREATE TABLE with_constraints1 (
    col_1 boolean NOT NULL DEFAULT false
);
CREATE TABLE with_constraints2 (
    col_1 boolean DEFAULT false NOT NULL
);


CREATE TABLE test_with_storage_param (
    col_1 boolean
) WITH (autovacuum_enabled=true);


CREATE TABLE test_with_storage_params (
    col_1 boolean
) WITH (autovacuum_enabled=true, vacuum_truncate=false);

-- Test out EXCLUDE constraints, as well as other more advanced index parameters on constraints

-- from https://www.postgresql.org/docs/15/rangetypes.html: basic usage
CREATE TABLE reservation (
    during tsrange,
    EXCLUDE USING gist (during WITH &&)
);
CREATE TABLE room_reservation (
    room text,
    during tsrange,
    EXCLUDE USING gist (room WITH =, during WITH &&)
);

-- all the gnarly options: not every option is valid, but this will parse successfully on PG 15.
CREATE TABLE no_using (
    field text,
    EXCLUDE (field WITH =) NOT DEFERRABLE INITIALLY IMMEDIATE NO INHERIT
);
CREATE TABLE many_options (
    field text,
    EXCLUDE USING gist (
        one WITH =,
        nulls_opclass nulls WITH =,
        nulls_last NULLS LAST WITH =,
        two COLLATE "en-US" opclass
            (opt1, opt2=5, opt3='str', ns.opt4, ns.opt5=6, ns.opt6='str', opt7=ASC)
            ASC NULLS FIRST WITH =,
        (two + 5) WITH =,
        myfunc(a, b) WITH =,
        myfunc_opclass(a, b) fop (opt=1, foo=2) WITH =,
        only_opclass opclass WITH =,
        desc_order DESC WITH =
    ) INCLUDE (a, b) WITH (idx_num = 5, idx_str = 'idx_value', idx_kw=DESC)
        USING INDEX TABLESPACE tblspc
        WHERE (field != 'def')
        DEFERRABLE INITIALLY DEFERRED
);
