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
