CREATE LANGUAGE plsample HANDLER plpgsql_call_handler;

CREATE TRUSTED PROCEDURAL LANGUAGE plsample2
    HANDLER pg_catalog.plpgsql_call_handler
    INLINE plpgsql_inline_handler
    VALIDATOR plpgsql_validator;

CREATE OR REPLACE LANGUAGE plsample HANDLER plpgsql_call_handler NO VALIDATOR;

CREATE PROCEDURAL LANGUAGE "PlSample" HANDLER plpgsql_call_handler INLINE plpgsql_inline_handler;

CREATE OR REPLACE TRUSTED LANGUAGE plpgsql;
