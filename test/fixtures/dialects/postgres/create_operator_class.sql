CREATE OPERATOR CLASS complex_abs_ops
    DEFAULT FOR TYPE complex USING btree AS
        OPERATOR 1 <,
        OPERATOR 2 <=,
        OPERATOR 3 =,
        OPERATOR 4 >=,
        OPERATOR 5 >,
        FUNCTION 1 complex_abs_cmp(complex, complex);

CREATE OPERATOR CLASS gist__int_ops
    DEFAULT FOR TYPE _int4 USING gist AS
        OPERATOR 3 &&,
        OPERATOR 6 = (anyarray, anyarray),
        OPERATOR 7 @>,
        OPERATOR 8 <@,
        OPERATOR 20 @@ (_int4, query_int),
        FUNCTION 1 g_int_consistent (internal, _int4, smallint, oid, internal),
        FUNCTION 2 g_int_union (internal, internal),
        FUNCTION 7 g_int_same (_int4, _int4, internal),
        STORAGE internal;

CREATE OPERATOR CLASS myschema.int4_custom_ops
    FOR TYPE int4 USING btree FAMILY integer_ops AS
        OPERATOR 1 < (int4, int4) FOR SEARCH,
        FUNCTION 1 (int4, int4) btint4cmp(int4, int4);

CREATE OPERATOR CLASS point_knn_ops
    FOR TYPE point USING gist AS
        OPERATOR 15 <-> (point, point) FOR ORDER BY float_ops,
        STORAGE box;
