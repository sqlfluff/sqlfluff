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
