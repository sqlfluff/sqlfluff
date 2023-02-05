CREATE UNIQUE INDEX title_idx ON films (title);

CREATE UNIQUE INDEX title_idx ON films (title) INCLUDE (director, rating);

CREATE INDEX title_idx ON films (title) WITH (deduplicate_items = 'off');

CREATE INDEX ON films ((lower(title)));

CREATE INDEX title_idx_german ON films (title COLLATE "de_DE");

CREATE INDEX title_idx_nulls_low ON films (title NULLS FIRST);

CREATE INDEX title_idx_nulls_high ON films (title NULLS LAST);

CREATE UNIQUE INDEX title_idx ON films (title) WITH (fillfactor = 70);

CREATE INDEX gin_idx ON documents_table USING GIN (locations) WITH (fastupdate = 'off');

CREATE INDEX code_idx ON films (code) TABLESPACE indexspace;

CREATE INDEX pointloc
    ON points USING gist (box(location,location));

CREATE INDEX CONCURRENTLY sales_quantity_index ON sales_table (quantity);

CREATE INDEX super_idx ON super_table USING btree(super_column DESC);

CREATE INDEX opclass_index ON schema.opclass_table (col varchar_pattern_ops);

CREATE INDEX opclass_index_with_parameters ON schema.opclass_table (col varchar_pattern_ops(p1='3', p2='4'));

CREATE UNIQUE INDEX tests_success_constraint ON tests (subject, target)
    WHERE success;

CREATE INDEX nulls_distinct_index ON documents_table USING GIN (locations)
     NULLS DISTINCT WITH (fastupdate = 'off');

CREATE INDEX nulls_not_distinct_index ON documents_table USING GIN (locations)
    NULLS NOT DISTINCT WITH (fastupdate = 'off');

CREATE INDEX code_idx ON films (code) TABLESPACE indexspace;
