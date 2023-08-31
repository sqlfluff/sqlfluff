GRANT OWNERSHIP ON SCHEMA MY_DATABASE.MY_SCHEMA TO ROLE MY_ROLE;

GRANT ROLE MY_ROLE TO ROLE MY_OTHER_ROLE;

grant use_any_role on integration external_oauth_1 to role1;

grant ownership on table myschema.mytable to role analyst;

grant ownership on all tables in schema public to role analyst;

grant ownership on all tables in schema mydb.public to role analyst;

grant ownership on all tables in schema mydb.public to role analyst copy current grants;

GRANT ROLE ROLENAME TO ROLE IDENTIFIER($THIS_ROLE);

GRANT OWNERSHIP ON ROLE TEST_ROLE TO ROLE DIFFERENT_ROLE;

grant all on all materialized views in database my_db to role analyst;
grant all on all file formats in database my_db to role analyst;
grant create temporary table on schema my_db.my_schema to role analyst;
grant all on future pipes in database my_db to role analyst;
grant all on future file formats in database my_db to role analyst;
grant all on future materialized views in database my_db to role analyst;
grant all on future pipes in database my_db to role analyst;
grant usage on all sequences in database my_db to role analyst;
grant all on all materialized views in database my_db to role analyst;
grant all on all sequences in database my_db to role analyst;
grant all on all functions in database my_db to role analyst;
grant all on all file formats in database my_db to role analyst;
grant all on all stages in database my_db to role analyst;
grant select on all views in database my_db to role analyst;

revoke role analyst from role sysadmin;

revoke select,insert on future tables in schema mydb.myschema from role role1;

revoke all privileges on function add5(number) from role analyst;

revoke grant option for operate on warehouse report_wh from role analyst;

revoke select on all tables in schema mydb.myschema from role analyst;

revoke operate on warehouse report_wh from role analyst;

revoke reference_usage on database database2 from share share1;

REVOKE OWNERSHIP ON ROLE TEST_ROLE FROM ROLE DIFFERENT_ROLE;

grant operate on warehouse report_wh to role analyst;
grant operate on warehouse report_wh to role analyst with grant option;
grant select on all tables in schema mydb.myschema to role analyst;
grant all privileges on function mydb.myschema.add5(number) to role analyst;
grant all privileges on function mydb.myschema.add5(string) to role analyst;
grant usage on procedure mydb.myschema.myprocedure(number) to role analyst;
grant create materialized view on schema mydb.myschema to role myrole;
grant select,insert on future tables in schema mydb.myschema to role role1;
grant usage on future schemas in database mydb to role role1;

grant usage on database database1 to share share1;
grant usage on schema database1.schema1 to share share1;
grant reference_usage on database database2 to share share1;
grant select on view view2 to share share1;
grant usage on database mydb to share share1;
grant usage on schema mydb.public to share share1;
grant usage on function mydb.shared_schema.function1 to share share1;
grant select on all tables in schema mydb.public to share share1;
grant usage on schema mydb.shared_schema to share share1;
grant select on view mydb.shared_schema.view1 to share share1;
grant select on view mydb.shared_schema.view3 to share share1;

grant role analyst to user user1;

revoke all privileges on procedure clean_schema(string) from role analyst;
revoke all privileges on function add5(string) from role analyst;

revoke select on view mydb.shared_schema.view1 from share share1;
revoke usage on schema mydb.shared_schema from share share1;
revoke select on all tables in schema mydb.public from share share1;
revoke usage on schema mydb.public from share share1;
revoke usage on database mydb from share share1;

grant apply masking policy on account to role my_role;
grant apply row access policy on account to role my_role;
grant apply session policy on account to role my_role;
grant apply tag on account to role my_role;
grant attach policy on account to role my_role;
grant execute task on account to role my_role;
grant import share on account to role my_role;
grant manage grants on account to role my_role;
grant monitor execution on account to role my_role;
grant monitor usage on account to role my_role;
grant override share restrictions on account to role my_role;
grant create account on account to role my_role;
grant create share on account to role my_role;
grant create network policy on account to role my_role;
grant create data exchange listing on account to role my_role;

GRANT MANAGE ACCOUNT SUPPORT CASES ON ACCOUNT TO ROLE my_role;
GRANT MANAGE ORGANIZATION SUPPORT CASES ON ACCOUNT TO ROLE my_role;
GRANT MANAGE USER SUPPORT CASES ON ACCOUNT TO ROLE my_role;
