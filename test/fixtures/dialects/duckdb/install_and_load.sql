INSTALL httpfs;

INSTALL 'httpfs';

FORCE INSTALL httpfs;

INSTALL h3 FROM community;

INSTALL spatial FROM core_nightly;

FORCE INSTALL h3 FROM community;

INSTALL custom_ext FROM 'http://my-extension-repository';

INSTALL '/path/to/httpfs.duckdb_extension';

LOAD httpfs;

LOAD 'httpfs';

LOAD '/path/to/httpfs.duckdb_extension';

SELECT install FROM install;
