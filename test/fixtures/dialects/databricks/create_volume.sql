-- Create volume `customer_vol`.
-- This throws exception if volume with name customer_vol already exists.
CREATE VOLUME customer_vol;

-- Create volume `customer_vol` only if volume with same name doesn't exist.
CREATE VOLUME IF NOT EXISTS customer_vol;

-- Create volume `customer_vol` only if volume with same name doesn't exist,
-- with a comment.
CREATE VOLUME IF NOT EXISTS customer_vol COMMENT 'This is customer volume';

-- Create external volume `customer_vol_external`
-- This throws exception if volume with name customer_vol_external
-- already exists.
CREATE EXTERNAL VOLUME customer_vol_external
LOCATION 's3://s3-path/';

-- Create external volume `customer_vol_external`
-- only if volume with same name doesn't exist, with a location.
CREATE EXTERNAL VOLUME IF NOT EXISTS customer_vol_external
LOCATION 's3://s3-path/';

-- Create external volume `customer_vol_external`
-- only if volume with same name doesn't exist, with a location and a comment.
CREATE EXTERNAL VOLUME IF NOT EXISTS customer_vol_external
LOCATION 's3://s3-path/'
COMMENT 'This is customer volume';
