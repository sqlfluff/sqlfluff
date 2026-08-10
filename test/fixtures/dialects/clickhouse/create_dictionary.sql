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

-- https://fiddle.clickhouse.com/a82027e0-c8b1-4240-a792-e536cabb883d
-- SOURCE, LAYOUT, LIFETIME
CREATE DICTIONARY test_db.test_dict (
  id UInt64,
  id2 UInt64,
  val String
)
PRIMARY KEY `id`, id2
SOURCE(NULL())
LAYOUT(COMPLEX_KEY_HASHED())
LIFETIME(100);

-- SOURCE, LAYOUT, LIFETIME, RANGE, COMMENT
CREATE OR REPLACE DICTIONARY test_db.test_dict (
  id UInt64,
  id2 UInt64,
  val String,
  discount_start_date Date,
  discount_end_date Date
)
PRIMARY KEY (`id`, "id2")
LIFETIME(100)
LAYOUT(COMPLEX_KEY_RANGE_HASHED())
SOURCE(NULL())
RANGE(MIN "discount_start_date" MAX discount_end_date)
COMMENT 'comment';

-- SOURCE, LAYOUT, LIFETIME, SETTINGS
CREATE OR REPLACE DICTIONARY test_db.test_dict (
  id UInt64,
  id2 UInt64,
  val String
)
PRIMARY KEY id, id2
SETTINGS(min_idle_time = 10)
LAYOUT(COMPLEX_KEY_HASHED())
SOURCE(CLICKHOUSE(HOST 'localhost' PORT 9000 USER 'default' PASSWORD '' QUERY $$
    SELECT 1 AS id, 1 AS id2, 'test' AS val
$$))
LIFETIME(100);

-- SOURCE, LAYOUT, LIFETIME, RANGE, SETTINGS
CREATE OR REPLACE DICTIONARY test_db.test_dict (
  id UInt64,
  id2 UInt64,
  val String,
  discount_start_date Date,
  discount_end_date Date
)
PRIMARY KEY (id, id2)
LIFETIME(MIN 10 MAX 100)
LAYOUT(COMPLEX_KEY_RANGE_HASHED())
SETTINGS(min_idle_time = 10)
RANGE(MIN `discount_start_date` MAX `discount_end_date`)
SOURCE(NULL());
