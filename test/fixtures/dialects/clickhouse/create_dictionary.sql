CREATE OR REPLACE DICTIONARY IF NOT EXISTS analytics.dict_countries
ON CLUSTER mycluster
(
    country_code String DEFAULT '' IS_OBJECT_ID,
    country_id UInt64,
    country_name String DEFAULT 'UNKNOWN',
    country_name_lower String EXPRESSION lower(country_name),
    region String,
    parent_code String DEFAULT '' HIERARCHICAL,
    is_active UInt8 DEFAULT 1 INJECTIVE
)
PRIMARY KEY country_code, country_id
SOURCE(CLICKHOUSE(HOST 'localhost' PORT 9000 USER 'default' PASSWORD '<PASSWORD>' TABLE 'dim_countries' DB 'analytics'))
LAYOUT(HASHED())
LIFETIME(MIN 300 MAX 600)
SETTINGS(min_idle_time = 10, max_block_size = 10000)
COMMENT 'Country dictionary with defaults and expressions';
