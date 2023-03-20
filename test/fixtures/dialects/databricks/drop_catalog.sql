-- Create a `vaccine` catalog
CREATE CATALOG vaccine COMMENT 'This catalog is used to maintain information about vaccines';

-- Drop the catalog and its schemas
DROP CATALOG vaccine CASCADE;

-- Drop the catalog using IF EXISTS and only if it is empty.
DROP CATALOG IF EXISTS vaccine RESTRICT;
