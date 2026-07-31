COMMENT ON TABLE myschema.mytab IS 'a table';

COMMENT ON COLUMN myschema.mytab.mycol IS 'a column';

COMMENT ON INDEX myschema.myidx IS 'an index';

COMMENT ON TABLE myschema.mytab (
    col1 IS 'first column',
    col2 IS 'second column'
);
