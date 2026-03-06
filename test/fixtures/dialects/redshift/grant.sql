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
