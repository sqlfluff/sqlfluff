-- System privileges
GRANT CREATE SCHEMA TO role1;
GRANT SELECT ANY TABLE TO user1 WITH ADMIN OPTION;
-- Object privileges
GRANT INSERT ON my_schema.my_table TO user1, role2;
GRANT SELECT ON VIEW my_schema.my_view TO user1;
-- Access on my_view for all users
GRANT SELECT ON my_schema.my_view TO PUBLIC;
-- Roles
GRANT role1 TO user1, user2 WITH ADMIN OPTION;
GRANT role2 TO role1;
-- Impersonation
GRANT IMPERSONATION ON user2 TO user1;
GRANT IMPERSONATION ON "user2" TO user1;
GRANT IMPERSONATION ON user2 TO "user1";
-- Connection
GRANT CONNECTION my_connection TO user1;
GRANT CONNECTION my_connection TO "ADMIN";
-- Access to connection details for certain script
GRANT ACCESS ON CONNECTION my_connection
FOR SCRIPT script1 TO user1;
GRANT ACCESS ON CONNECTION "my_connection"
FOR SCRIPT "script1" TO "user1";

REVOKE CREATE SCHEMA FROM role1,user3;
-- Object privileges
REVOKE SELECT, INSERT ON my_schema.my_table FROM user1, role2;
REVOKE ALL PRIVILEGES ON VIEW my_schema.my_view FROM PUBLIC;
-- Role
REVOKE role1 FROM user1, user2;
-- Impersonation
REVOKE IMPERSONATION ON user2 FROM user1;
-- Connections
REVOKE CONNECTION my_connection FROM user1;
REVOKE CONNECTION my_connection FROM "ADMIN";
