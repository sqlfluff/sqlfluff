-- Test various forms of quoted data types
CREATE TABLE foo (
    pk int PRIMARY KEY,
    quoted_name "custom udt",
    qualified_name sch.qualified,
    quoted_qualified "my schema".qualified,
    more_quoted "my schema"."custom udt",
    quoted_udt sch."custom udt"
);
