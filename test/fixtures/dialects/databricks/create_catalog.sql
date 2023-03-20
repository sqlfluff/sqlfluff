-- Create catalog `customer_cat`.
-- This throws exception if catalog with name customer_cat already exists.
CREATE CATALOG customer_cat;

-- Create catalog `customer_cat` only if catalog with same name doesn't exist.
CREATE CATALOG IF NOT EXISTS customer_cat;

-- Create catalog `customer_cat` only if catalog with same name doesn't exist, with a comment.
CREATE CATALOG IF NOT EXISTS customer_cat COMMENT 'This is customer catalog';
