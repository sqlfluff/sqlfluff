ALTER USER my_user SET AUTHENTICATION POLICY my_db.my_schema.my_auth_policy;

ALTER USER IF EXISTS my_user SET AUTHENTICATION POLICY my_auth_policy FORCE;

ALTER USER my_user UNSET AUTHENTICATION POLICY;

ALTER USER my_user SET PASSWORD POLICY my_db.my_schema.my_password_policy;

ALTER USER my_user UNSET PASSWORD POLICY;

ALTER USER my_user SET SESSION POLICY my_db.my_schema.my_session_policy;

ALTER USER my_user UNSET SESSION POLICY;
