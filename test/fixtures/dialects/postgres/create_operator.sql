CREATE OPERATOR >=(
    LEFTARG = semantic_version,
    RIGHTARG = semantic_version,
    PROCEDURE = semantic_version_ge,
    COMMUTATOR = <=
);

CREATE OPERATOR === (
    LEFTARG = box,
    RIGHTARG = box,
    FUNCTION = area_equal_function,
    COMMUTATOR = ===,
    NEGATOR = !==,
    RESTRICT = area_restriction_function,
    JOIN = area_join_function,
    HASHES, MERGES
);

-- pg_dump writes the schema of the operator, and `OPERATOR(schema.name)`
CREATE OPERATOR app.=== (
    FUNCTION = app.int_eq,
    LEFTARG = integer,
    RIGHTARG = integer,
    COMMUTATOR = OPERATOR(app.===),
    NEGATOR = OPERATOR(app.!==)
);

CREATE OPERATOR <<-> (
    LEFTARG = double precision,
    RIGHTARG = double precision,
    FUNCTION = float8_distance,
    COMMUTATOR = <<->
);

CREATE OPERATOR ~~~ (
    LEFTARG = character varying,
    RIGHTARG = text[],
    FUNCTION = varchar_in_array
);

CREATE OPERATOR public.@@ (
    RIGHTARG = timestamp with time zone,
    FUNCTION = age_of
);

CREATE OPERATOR public.## (
    LEFTARG = point,
    RIGHTARG = lseg,
    FUNCTION = close_ps
);
