CREATE
OR REPLACE PYTHON3 SCALAR SCRIPT MYSCHEMA.MYPYTHONSCRIPT(
    JSON_STR VARCHAR(2000000),
    LANGUAGE_KEY VARCHAR(50),
    TXT_KEY VARCHAR(50)
) EMITS (
    X VARCHAR(2000000)
)
AS
"""
/*====================================================================
    e.g.:
    SELECT MYSCHEMA.MYPYTHONSCRIPT(
            '[{"@lang":"de-DE","$":"Krztxt"}, {"@lang":"en-GB","$":"Shrttxt"}]',
            '@lang',
            '$'
        );
 ====================================================================*/
"""
def run (ctx):
    pass
/
