DROP SECRET my_secret;

DROP SECRET IF EXISTS my_db.my_schema.my_secret;

DESCRIBE SECRET my_secret;

DESC SECRET my_db.my_schema.my_secret;

SHOW SECRETS;

SHOW SECRETS LIKE 'my%' IN SCHEMA my_db.my_schema;

GRANT USAGE ON SECRET my_secret TO ROLE my_role;

GRANT READ ON SECRET my_db.my_schema.my_secret TO ROLE my_role;

GRANT USAGE ON ALL SECRETS IN SCHEMA my_db.my_schema TO ROLE my_role;

GRANT USAGE ON FUTURE SECRETS IN SCHEMA my_db.my_schema TO ROLE my_role;

REVOKE USAGE ON SECRET my_secret FROM ROLE my_role;

REVOKE USAGE ON ALL SECRETS IN SCHEMA my_db.my_schema FROM ROLE my_role;

REVOKE USAGE ON FUTURE SECRETS IN SCHEMA my_db.my_schema FROM ROLE my_role;
