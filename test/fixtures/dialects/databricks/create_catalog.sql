-- Create catalog `customer_cat`.
-- This throws exception if catalog with name customer_cat already exists.
CREATE CATALOG customer_cat;

-- Create catalog `customer_cat` only if catalog with same name doesn't exist.
CREATE CATALOG IF NOT EXISTS customer_cat;

-- Create catalog `customer_cat` only if catalog with same name doesn't exist, with a comment.
CREATE CATALOG IF NOT EXISTS customer_cat COMMENT 'This is customer catalog';

-- Create catalog `customer_cat` with a storage root location.
CREATE CATALOG customer_cat MANAGED LOCATION 's3://depts/customers';

-- The optional clauses may appear in either order.
CREATE CATALOG IF NOT EXISTS customer_cat
    COMMENT 'This is customer catalog'
    MANAGED LOCATION 's3://depts/customers';

-- The rest of the clause set.
CREATE CATALOG customer_cat USING SHARE provider.share;

CREATE CATALOG customer_cat RETAIN DROPPED FOR 30 DAYS;

CREATE CATALOG customer_cat RETAIN DROPPED FOR 1 HOUR;

CREATE CATALOG customer_cat DEFAULT COLLATION UTF8_BINARY;

CREATE CATALOG customer_cat OPTIONS (k = 'v');

-- The foreign catalog production.
CREATE FOREIGN CATALOG foreign_cat USING CONNECTION conn OPTIONS (k = 'v');

CREATE FOREIGN CATALOG IF NOT EXISTS foreign_cat
    USING CONNECTION conn
    OPTIONS (k = 'v');

CREATE FOREIGN CATALOG foreign_cat
    USING CONNECTION conn
    COMMENT 'a foreign catalog'
    OPTIONS (k = 'v');
