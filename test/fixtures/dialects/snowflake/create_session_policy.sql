-- Basic session policy
CREATE SESSION POLICY my_session_policy
  SESSION_IDLE_TIMEOUT_MINS = 30;

-- Session policy with all options
CREATE OR REPLACE SESSION POLICY IF NOT EXISTS my_session_policy
  SESSION_IDLE_TIMEOUT_MINS = 60
  SESSION_UI_IDLE_TIMEOUT_MINS = 30
  COMMENT = 'production session policy';
