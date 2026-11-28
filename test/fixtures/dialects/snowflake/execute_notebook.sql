EXECUTE NOTEBOOK my_notebook();

EXECUTE NOTEBOOK my_db.public.my_notebook();

EXECUTE NOTEBOOK my_notebook('parameter_string a,b,c,d');

EXECUTE NOTEBOOK my_database.public.my_notebook(
    'parameter_string a,b,c,d',
    'target_database=PROD_DB'
);
