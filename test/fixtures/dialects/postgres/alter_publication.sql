-- More thorough testing of the PublicationObjectsSegment is in postgres_create_publication.sql.

ALTER PUBLICATION abc ADD TABLE def;

ALTER PUBLICATION abc ADD TABLE def, TABLE ghi;

ALTER PUBLICATION abc ADD TABLE def, ghi*, ONLY jkl, ONLY (mno);

ALTER PUBLICATION abc SET TABLE def, ghi, TABLES IN SCHEMA y, z, CURRENT_SCHEMA;

ALTER PUBLICATION abc SET (publish = 'insert,update', publish_via_partition_root = TRUE);

ALTER PUBLICATION abc OWNER TO bob;

ALTER PUBLICATION abc OWNER TO CURRENT_ROLE;

ALTER PUBLICATION abc OWNER TO CURRENT_USER;

ALTER PUBLICATION abc OWNER TO SESSION_USER;

ALTER PUBLICATION abc RENAME TO def;

-- examples from https://www.postgresql.org/docs/15/sql-alterpublication.html

ALTER PUBLICATION noinsert SET (publish = 'update, delete');

ALTER PUBLICATION mypublication ADD TABLE users (user_id, firstname), departments;

ALTER PUBLICATION mypublication SET TABLE users (user_id, firstname, lastname), TABLE departments;

ALTER PUBLICATION sales_publication ADD TABLES IN SCHEMA marketing, sales;

ALTER PUBLICATION production_publication ADD TABLE users, departments, TABLES IN SCHEMA production;
