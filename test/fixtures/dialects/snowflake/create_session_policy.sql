CREATE SESSION POLICY my_session_policy;

CREATE OR REPLACE SESSION POLICY my_session_policy
    SESSION_IDLE_TIMEOUT_MINS = 30
    SESSION_UI_IDLE_TIMEOUT_MINS = 30
    COMMENT = 'session policy';

CREATE SESSION POLICY IF NOT EXISTS my_db.my_schema.my_session_policy
    SESSION_MAX_LIFESPAN_MINS = 1440
    SESSION_UI_MAX_LIFESPAN_MINS = 1440
    ALLOWED_SECONDARY_ROLES = ()
    COMMENT = 'session policy';

CREATE SESSION POLICY my_db.my_schema.my_session_policy
    ALLOWED_SECONDARY_ROLES = ('ALL');

CREATE SESSION POLICY my_db.my_schema.my_session_policy
    ALLOWED_SECONDARY_ROLES = ('my_role_1', 'my_role_2')
    BLOCKED_SECONDARY_ROLES = ('my_role_3');
