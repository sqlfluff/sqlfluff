-- Both conversion directions, with explicit function argument types.
CREATE TRANSFORM FOR hstore LANGUAGE plpython3u (
    FROM SQL WITH FUNCTION hstore_to_plpython(internal),
    TO SQL WITH FUNCTION plpython_to_hstore(internal)
);

-- Replacement and schema-qualified type and function names.
CREATE OR REPLACE TRANSFORM FOR public.hstore LANGUAGE plpython3u (
    FROM SQL WITH FUNCTION public.hstore_to_plpython(internal),
    TO SQL WITH FUNCTION public.plpython_to_hstore(internal)
);

-- Either direction can be supplied on its own; function signatures are optional.
CREATE TRANSFORM FOR hstore LANGUAGE plpython3u (
    FROM SQL WITH FUNCTION hstore_to_plpython
);
CREATE TRANSFORM FOR hstore LANGUAGE plpython3u (
    TO SQL WITH FUNCTION plpython_to_hstore
);

-- Quoted identifiers and an array type.
CREATE TRANSFORM FOR "app"."Custom Type" LANGUAGE "plpython3u" (
    FROM SQL WITH FUNCTION "app"."From SQL"(internal)
);
CREATE TRANSFORM FOR integer[] LANGUAGE plpython3u (
    TO SQL WITH FUNCTION array_from_python(internal)
);
