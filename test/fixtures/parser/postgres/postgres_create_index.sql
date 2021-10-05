CREATE UNIQUE INDEX title_idx ON films (title);

CREATE UNIQUE INDEX title_idx ON films (title) INCLUDE (director, rating);

CREATE INDEX title_idx ON films (title) WITH (deduplicate_items = 'off');

CREATE INDEX ON films ((lower(title)));

CREATE INDEX title_idx_german ON films (title COLLATE "de_DE");

CREATE INDEX title_idx_nulls_low ON films (title NULLS FIRST);

CREATE UNIQUE INDEX title_idx ON films (title) WITH (fillfactor = 70);

CREATE INDEX gin_idx ON documents_table USING GIN (locations) WITH (fastupdate = 'off');

CREATE INDEX code_idx ON films (code) TABLESPACE indexspace;

CREATE INDEX pointloc
    ON points USING gist (box(location,location));

CREATE INDEX CONCURRENTLY sales_quantity_index ON sales_table (quantity);
