GRANT OWNERSHIP ON SCHEMA MY_DATABASE.MY_SCHEMA TO ROLE MY_ROLE;

GRANT ROLE MY_ROLE TO ROLE MY_OTHER_ROLE;

grant use_any_role on integration external_oauth_1 to role1;

grant ownership on table myschema.mytable to role analyst;

grant ownership on all tables in schema public to role analyst;

grant ownership on all tables in schema mydb.public to role analyst;

grant ownership on all tables in schema mydb.public to role analyst copy current grants;

GRANT ROLE ROLENAME TO ROLE IDENTIFIER($THIS_ROLE);

GRANT OWNERSHIP ON ROLE TEST_ROLE TO ROLE DIFFERENT_ROLE;

GRANT ALL ON ALL MATERIALIZED VIEWS IN DATABASE my_db TO ROLE analyst;

GRANT ALL ON ALL FILE FORMATS IN DATABASE my_db TO ROLE analyst;

GRANT CREATE TEMPORARY TABLE ON SCHEMA my_db.my_schema TO ROLE analyst;

GRANT ALL ON FUTURE PIPES IN DATABASE my_db TO ROLE analyst;

GRANT ALL ON FUTURE FILE FORMATS IN DATABASE my_db TO ROLE analyst;

GRANT ALL ON FUTURE MATERIALIZED VIEWS IN DATABASE my_db TO ROLE analyst;

GRANT ALL ON FUTURE PIPES IN DATABASE my_db TO ROLE analyst;

GRANT USAGE ON ALL SEQUENCES IN DATABASE my_db TO ROLE analyst;

GRANT ALL ON ALL MATERIALIZED VIEWS IN DATABASE my_db TO ROLE analyst;

GRANT ALL ON ALL SEQUENCES IN DATABASE my_db TO ROLE analyst;

GRANT ALL ON ALL FUNCTIONS IN DATABASE my_db TO ROLE analyst;

GRANT ALL ON ALL FILE FORMATS IN DATABASE my_db TO ROLE analyst;

GRANT ALL ON ALL STAGES IN DATABASE my_db TO ROLE analyst;

GRANT SELECT ON ALL VIEWS IN DATABASE my_db TO ROLE analyst;

revoke role analyst from role sysadmin;

revoke select,insert on future tables in schema mydb.myschema from role role1;

revoke all privileges on function add5(number) from role analyst;

revoke grant option for operate on warehouse report_wh from role analyst;

revoke select on all tables in schema mydb.myschema from role analyst;

revoke operate on warehouse report_wh from role analyst;

revoke reference_usage on database database2 from share share1;

REVOKE OWNERSHIP ON ROLE TEST_ROLE FROM ROLE DIFFERENT_ROLE;
