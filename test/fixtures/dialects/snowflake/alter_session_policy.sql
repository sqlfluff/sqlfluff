-- Rename
ALTER SESSION POLICY my_session_policy RENAME TO new_session_policy;

-- Set properties
ALTER SESSION POLICY my_session_policy SET
  SESSION_IDLE_TIMEOUT_MINS = 45
  SESSION_UI_IDLE_TIMEOUT_MINS = 15;

-- Unset properties
ALTER SESSION POLICY my_session_policy UNSET SESSION_IDLE_TIMEOUT_MINS;

ALTER SESSION POLICY my_session_policy UNSET COMMENT;
