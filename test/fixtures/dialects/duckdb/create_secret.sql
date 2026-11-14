-- https://duckdb.org/docs/stable/sql/statements/create_secret
CREATE SECRET (TYPE s3);

CREATE SECRET s3_chain (
    TYPE s3,
    PROVIDER credential_chain,
    CHAIN 'env;config'
);

CREATE OR REPLACE SECRET "example secret" (
    TYPE http,
    PROVIDER config,
    SCOPE 'https://example.com/'
);

CREATE TEMPORARY SECRET temporary_secret (TYPE s3, REGION 'us-east-1');

CREATE PERSISTENT SECRET persistent_secret IN local_file (
    TYPE s3,
    PROVIDER config,
    USE_SSL true,
    REGION 'us-east-1'
);

CREATE SECRET IF NOT EXISTS existing_secret (TYPE s3, PROVIDER credential_chain);

CREATE SECRET IN memory (TYPE s3, PROVIDER credential_chain);

CREATE SECRET connection_secret IN connection (
    TYPE http,
    EXTRA_HTTP_HEADERS MAP {'X-Example': 'sample'}
);

create secret "quoted name" (type 'http', provider 'config');
