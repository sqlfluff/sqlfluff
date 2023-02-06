ATTACH RLS POLICY policy_concerts ON tickit_category_redshift TO ROLE analyst, ROLE dbadmin;

ATTACH RLS POLICY policy_name ON TABLE table_name TO PUBLIC;
