INSTALL httpfs;

INSTALL 'httpfs';

FORCE INSTALL httpfs;

INSTALL h3 FROM community;

INSTALL spatial FROM core_nightly;

FORCE INSTALL h3 FROM community;

INSTALL custom_ext FROM 'http://my-extension-repository';

INSTALL '/path/to/httpfs.duckdb_extension';

INSTALL spatial VERSION 'v1.1.8';

INSTALL spatial FROM core VERSION 'v1.1.8';

FORCE INSTALL 'spatial' FROM 'https://extensions.duckdb.org' VERSION 'v1.1.8';

INSTALL spatial VERSION latest;

LOAD httpfs;

LOAD 'httpfs';

LOAD '/path/to/httpfs.duckdb_extension';

SELECT install FROM install;
