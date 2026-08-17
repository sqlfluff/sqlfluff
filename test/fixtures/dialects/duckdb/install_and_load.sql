-- Install and load DuckDB extensions.
-- https://duckdb.org/docs/stable/sql/statements/load_and_install

INSTALL spatial;

INSTALL httpfs;

LOAD spatial;

LOAD httpfs;

-- Force a re-install (e.g. to switch repositories).
FORCE INSTALL spatial;

-- Install from a named repository (an alias such as community or core_nightly).
INSTALL h3 FROM community;

FORCE INSTALL httpfs FROM core_nightly;

-- Install from a direct URL, provided as a single-quoted string.
INSTALL spatial FROM 'https://some.custom/repository';

-- Install a local extension from a single-quoted file path.
INSTALL 'path/to/spatial.duckdb_extension';

LOAD 'path/to/spatial.duckdb_extension';
