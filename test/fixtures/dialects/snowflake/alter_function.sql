ALTER FUNCTION IF EXISTS function1(number) RENAME TO function2;
ALTER FUNCTION IF EXISTS function2(number) SET SECURE;
ALTER FUNCTION function3() UNSET COMMENT;

ALTER function function1(FLOAT_PARAM1 FLOAT)
SET TAG TAG1 = 'value1', TAG2 = 'value2', TAG3 = 'value3';

ALTER function function1()
UNSET TAG TAG1, TAG2, TAG3;

ALTER function function1()
SET COMMENT = 'just a comment';

ALTER function function1()
UNSET COMMENT;

ALTER FUNCTION example_function()
SET
    EXTERNAL_ACCESS_INTEGRATIONS = (my_external_access_integration),
    LOG_LEVEL = DEBUG,
    TRACE_LEVEL = ON_EVENT,
    SECRETS = ('cred' = oauth_token),
    COMMENT = 'just a comment'
;

ALTER FUNCTION example_function()
SET TAG TAG1 = 'value1', TAG2 = 'value2', TAG3 = 'value3',
    EXTERNAL_ACCESS_INTEGRATIONS = (my_external_access_integration),
    LOG_LEVEL = DEBUG,
    TRACE_LEVEL = ON_EVENT,
    SECRETS = ('cred' = oauth_token),
    COMMENT = 'just a comment'
;
