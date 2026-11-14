create foreign data wrapper stripe_wrapper
    handler stripe_fdw_handler
    validator stripe_fdw_validator;

CREATE FOREIGN DATA WRAPPER dummy;

CREATE FOREIGN DATA WRAPPER no_functions NO HANDLER NO VALIDATOR;

-- The clauses can come in any order, and the functions can be schema-qualified
CREATE FOREIGN DATA WRAPPER qualified
    VALIDATOR ext.my_validator
    HANDLER ext.my_handler;

CREATE FOREIGN DATA WRAPPER with_options
    HANDLER postgres_fdw_handler
    OPTIONS (debug 'true', retries '3');
