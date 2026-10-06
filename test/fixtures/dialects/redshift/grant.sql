-- Single group grant
GRANT SELECT, DELETE ON salesshare TO GROUP developer;

-- Multiple groups grant (issue: parse error when using multiple GROUP targets)
GRANT SELECT, DELETE ON salesshare TO GROUP developer, GROUP analyst;

-- Multiple privileges to multiple groups
GRANT SELECT, INSERT, UPDATE ON TABLE employees TO GROUP managers, GROUP analysts;

-- Grant with PUBLIC
GRANT SELECT ON TABLE public_data TO PUBLIC;

-- Grant with single user
GRANT SELECT ON TABLE secret_data TO USER admin_user;

-- Grant to role
GRANT SELECT ON TABLE data TO ROLE analyst_role;

GRANT SELECT ON TABLE data TO ROLE analyst_role, TO ROLE second_role;

GRANT ALL ON TABLE qa_tickit.sales TO GROUP qa_users, GROUP ro_users;

GRANT ALL ON SCHEMA qa_tickit TO schema_user;

GRANT SELECT(cust_name, cust_phone) ON cust_profile TO user1;

GRANT ROLE sample_role1 TO user1 WITH ADMIN OPTION;
GRANT ROLE sample_role1 TO user2;

-- Scoped permissions
GRANT USAGE FOR SCHEMAS IN DATABASE "analytics" TO "dev_user";
GRANT ALL FOR SCHEMAS IN DATABASE "analytics" TO ROLE "developers";
GRANT ALL PRIVILEGES FOR SCHEMAS IN DATABASE "analytics" TO ROLE "developers";

GRANT SELECT, UPDATE, DROP FOR TABLES IN SCHEMA "logistics" TO "dev_user";
GRANT ALL FOR TABLES IN SCHEMA "logistics" TO "dev_user";
GRANT ALL PRIVILEGES FOR TABLES IN DATABASE "analytics" TO "dev_user";

GRANT EXECUTE FOR FUNCTIONS IN SCHEMA "logistics" TO "dev_user";
GRANT ALL PRIVILEGES FOR FUNCTIONS IN DATABASE "analytics" TO ROLE "developers";

GRANT USAGE FOR LANGUAGES IN DATABASE "analytics" TO "dev_user";

GRANT CREATE FOR COPY JOBS IN DATABASE "analytics" TO "dev_user";
GRANT ALL PRIVILEGES FOR COPY JOBS IN DATABASE "analytics" TO ROLE "developers";

GRANT ALTER, DROP FOR TEMPLATES IN SCHEMA "logistics" TO "dev_user" WITH GRANT OPTION;
GRANT ALL PRIVILEGES FOR TEMPLATES IN DATABASE "analytics" TO "dev_user";
