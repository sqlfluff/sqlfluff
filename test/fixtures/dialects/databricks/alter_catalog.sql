-- Transfer ownership of the catalog to another user
ALTER CATALOG some_cat OWNER TO `alf@melmak.et`;

-- SET is allowed as an optional keyword
ALTER CATALOG some_cat SET OWNER TO `alf@melmak.et`;
