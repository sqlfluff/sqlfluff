CREATE FOREIGN TABLE foreign_table (
    simple_column integer,
    column_with_options char(5) OPTIONS (a 'foo', b 'bar'),
    column_with_collate text COLLATE "de_DE",
    column_with_not_null_constraint date NOT NULL,
    column_with_null_constraint varchar(50) NULL,
    column_with_check_constraint float CHECK (column_with_check_constraint > 0.0),
    column_with_default_constraint timestamp DEFAULT CURRENT_TIMESTAMP,
    column_with_generated_constraint bigint GENERATED ALWAYS AS (simple_column * 2) STORED,
    column_with_more_than_one_constraint int NOT NULL CHECK (column_with_more_than_one_constraint > 0),
    column_with_options_and_collate char(5) OPTIONS (a 'foo', b 'bar') COLLATE "es_ES",
    column_with_options_and_constraint char(5) OPTIONS (a 'foo', b 'bar') NOT NULL,
    column_with_collate_and_constraint char(5) COLLATE "de_DE" NOT NULL,
    column_with_options_collate_and_constraint char(5) OPTIONS (a 'foo', b 'bar') COLLATE "de_DE" NOT NULL,
    CHECK (simple_column > 0),
    CHECK (simple_column < 10) NO INHERIT,
    CONSTRAINT named_table_constraint CHECK (column_with_options <> ''),
    CONSTRAINT named_table_constraint_no_inherit CHECK (column_with_collate <> '') NO INHERIT
)
SERVER a_server;

CREATE FOREIGN TABLE IF NOT EXISTS foreign_table_that_might_already_exist (
    simple_column integer
)
SERVER a_server;

CREATE FOREIGN TABLE foreign_table_that_inherits (
    simple_column integer
)
INHERITS ( another_table )
SERVER a_server;

CREATE FOREIGN TABLE IF NOT EXISTS foreign_table_that_inherits_that_might_already_exist (
    simple_column integer
)
INHERITS ( another_table )
SERVER a_server;

CREATE FOREIGN TABLE foreign_table_with_options (
    simple_column integer
)
SERVER a_server
OPTIONS (c 'baz');

CREATE FOREIGN TABLE IF NOT EXISTS foreign_table_with_options_that_might_already_exist (
    simple_column integer
)
SERVER a_server
OPTIONS (c 'baz');

CREATE FOREIGN TABLE foreign_table_that_inherits_and_has_options (
    simple_column integer
)
INHERITS ( another_table )
SERVER a_server
OPTIONS (c 'baz');

CREATE FOREIGN TABLE IF NOT EXISTS foreign_table_that_inherits_and_has_options_that_might_already_exist (
    simple_column integer
)
INHERITS ( another_table )
SERVER a_server
OPTIONS (c 'baz');

CREATE FOREIGN TABLE foreign_table_partition_in
    PARTITION OF another_table FOR VALUES IN ('2016-07-01', '2016-08-01')
    SERVER a_server;

CREATE FOREIGN TABLE foreign_table_partition_from_min_to_max
    PARTITION OF another_table FOR VALUES FROM ('2016-07-01') TO ('2016-08-01')
    SERVER a_server;

CREATE FOREIGN TABLE foreign_table_partition_with
    PARTITION OF another_table FOR VALUES WITH ( MODULUS 2, REMAINDER 0)
    SERVER a_server;

CREATE FOREIGN TABLE IF NOT EXISTS foreign_table_partition_in_that_might_already_exist
    PARTITION OF another_table FOR VALUES IN ('2016-07-01', '2016-08-01')
    SERVER a_server;

CREATE FOREIGN TABLE IF NOT EXISTS foreign_table_partition_from_min_to_max_that_might_already_exist
    PARTITION OF another_table FOR VALUES FROM ('2016-07-01') TO ('2016-08-01')
    SERVER a_server;

CREATE FOREIGN TABLE IF NOT EXISTS foreign_table_partition_with_that_might_already_exist
    PARTITION OF another_table FOR VALUES WITH ( MODULUS 2, REMAINDER 0)
    SERVER a_server;

CREATE FOREIGN TABLE foreign_table_partition_in_with_options
    PARTITION OF another_table FOR VALUES IN ('2016-07-01', '2016-08-01')
    SERVER a_server
    OPTIONS (foo 'bar');

CREATE FOREIGN TABLE foreign_table_partition_from_min_to_max_with_options
    PARTITION OF another_table FOR VALUES FROM ('2016-07-01') TO ('2016-08-01')
    SERVER a_server
    OPTIONS (foo 'bar');

CREATE FOREIGN TABLE foreign_table_partition_with_with_options
    PARTITION OF another_table FOR VALUES WITH ( MODULUS 2, REMAINDER 0)
    SERVER a_server
    OPTIONS (foo 'bar');

CREATE FOREIGN TABLE foreign_table_partition_in_with_columns
    PARTITION OF another_table (
        simple_column,
        column_with_options WITH OPTIONS,
        column_with_not_null_constraint NOT NULL,
        column_with_null_constraint NULL,
        column_with_check_constraint CHECK (column_with_check_constraint > 0.0),
        column_with_default_constraint DEFAULT CURRENT_TIMESTAMP,
        column_with_generated_constraint GENERATED ALWAYS AS (simple_column * 2) STORED,
        column_with_more_than_one_constraint NOT NULL CHECK (column_with_more_than_one_constraint > 0),
        column_with_options_and_not_null_constraint WITH OPTIONS NOT NULL,
        CHECK (simple_column > 0),
        CHECK (simple_column < 10) NO INHERIT,
        CONSTRAINT named_table_constraint CHECK (column_with_options <> ''),
        CONSTRAINT named_table_constraint_no_inherit CHECK (column_with_options_and_not_null_constraint <> '')  NO INHERIT
    )
    FOR VALUES IN ('2016-07-01', '2016-08-01')
    SERVER a_server;

CREATE FOREIGN TABLE foreign_table_partition_with_from_min_to_max_with_columns
    PARTITION OF another_table (
        simple_column
    )
    FOR VALUES FROM ('2016-07-01') TO ('2016-08-01')
    SERVER a_server;

CREATE FOREIGN TABLE foreign_table_partition_with_with_columns
    PARTITION OF another_table (
        simple_column
    )
    FOR VALUES WITH ( MODULUS 2, REMAINDER 0)
    SERVER a_server;
