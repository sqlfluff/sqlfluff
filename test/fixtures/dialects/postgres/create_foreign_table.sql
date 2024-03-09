CREATE FOREIGN TABLE foreign_table (
    code        char(5) NOT NULL,
    title       varchar(40) NOT NULL,
    did         integer NOT NULL,
    date_prod   date,
    kind        varchar(10),
    len         interval
)
SERVER a_server;

CREATE FOREIGN TABLE IF NOT EXISTS foreign_table_that_might_already_exist (
    code        char(5) NOT NULL,
    title       varchar(40) NOT NULL,
    did         integer NOT NULL,
    date_prod   date,
    kind        varchar(10),
    len         interval
)
SERVER a_server;

CREATE FOREIGN TABLE foreign_table_that_inherits (
    code        char(5) NOT NULL,
    title       varchar(40) NOT NULL,
    did         integer NOT NULL,
    date_prod   date,
    kind        varchar(10),
    len         interval
)
INHERITS ( another_table )
SERVER a_server;

CREATE FOREIGN TABLE foreign_table_with_options (
    code        char(5) NOT NULL,
    title       varchar(40) NOT NULL,
    did         integer NOT NULL,
    date_prod   date,
    kind        varchar(10),
    len         interval
)
SERVER a_server
OPTIONS (foo 'bar');

CREATE FOREIGN TABLE foreign_table_partition
    PARTITION OF another_table FOR VALUES FROM ('2016-07-01') TO ('2016-08-01')
    SERVER a_server;

CREATE FOREIGN TABLE IF NOT EXISTS foreign_table_partition_that_might_already_exist
    PARTITION OF another_table FOR VALUES FROM ('2016-07-01') TO ('2016-08-01')
    SERVER a_server;

CREATE FOREIGN TABLE foreign_table_partition_with_options
    PARTITION OF another_table FOR VALUES FROM ('2016-07-01') TO ('2016-08-01')
    SERVER a_server
    OPTIONS (foo 'bar');

CREATE FOREIGN TABLE foreign_table_partition_with_columns
    PARTITION OF another_table (
        code        NOT NULL,
        title       NOT NULL,
        did         NOT NULL,
        date_prod,
        kind,
        len
    )
    FOR VALUES FROM ('2016-07-01') TO ('2016-08-01')
    SERVER a_server;
